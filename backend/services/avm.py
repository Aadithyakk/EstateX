from typing import Dict, Any, List, Optional
from ..utils.parsing import parse_storey_mid, parse_remaining_lease, derive_dates
import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False


class AVMService:
    def __init__(self, bundle: Dict[str, Any]):
        # bundle expected to contain: preprocessor, model, feature_columns, metadata(optional)
        self.bundle = bundle
        self.preprocessor = bundle.get("preprocessor")
        self.model = bundle.get("model")
        self._shap_explainer = None
        self._init_shap_explainer()
        # Determine feature column ordering. Support several bundle shapes.
        if bundle.get("feature_columns"):
            self.feature_columns = bundle.get("feature_columns", [])
        else:
            numeric = bundle.get("numeric_cols") or bundle.get("numeric_columns") or []
            categorical = bundle.get("categorical_cols") or bundle.get("categorical_columns") or []
            self.feature_columns = list(numeric) + list(categorical)
        self.metadata = bundle.get("metadata", {})

    def _init_shap_explainer(self):
        """Initialize SHAP explainer if available."""
        if not SHAP_AVAILABLE or not self.model:
            return
        try:
            self._shap_explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.warning(f"SHAP explainer init failed: {e}. Explainability will be unavailable.")

    def featurize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # derive fields from raw inputs
        storey_mid = parse_storey_mid(payload.get("storey_range"))
        remaining_lease = parse_remaining_lease(payload.get("remaining_lease") or payload.get("remaining_lease_years"))
        lease_start, txn_year, txn_month, txn_quarter = derive_dates(payload.get("lease_commence_date", ""), payload.get("txn_date"))

        # ensure all derived fields are properly typed as numeric
        lease_start = int(lease_start) if lease_start is not None else None
        remaining_lease = int(remaining_lease) if remaining_lease is not None else None
        storey_mid = float(storey_mid) if storey_mid is not None else None
        txn_year = int(txn_year) if txn_year is not None else None
        txn_month = int(txn_month) if txn_month is not None else None
        txn_quarter = int(txn_quarter) if txn_quarter is not None else None
        
        # derived features (assume 99-year lease if lease_commence_year is known)
        lease_end_year = None
        flat_age_at_txn = None
        if lease_start is not None:
            lease_end_year = lease_start + 99
        if lease_start is not None and txn_year is not None:
            flat_age_at_txn = txn_year - lease_start

        # build features dict with all original fields plus derived ones
        features = payload.copy()
        features.update({
            "storey_mid": storey_mid,
            "remaining_lease_years": remaining_lease,
            "lease_commence_year": lease_start,
            "txn_year": txn_year,
            "txn_month": txn_month,
            "txn_quarter": txn_quarter,
            "lease_end_year": lease_end_year,
            "flat_age_at_txn": flat_age_at_txn,
        })

        # Raw columns that should not be passed to preprocessor (they are converted to derived numeric columns)
        DROP_COLS = {"month", "storey_range", "remaining_lease", "lease_commence_date", "txn_date"}

        # Build normalized dict keyed by feature_columns; map variant names
        normalized = {}
        for col in self.feature_columns:
            val = None
            
            # 1. direct key match (but avoid raw string columns that were derived)
            if col in features and col not in DROP_COLS:
                val = features[col]
            # 2. try common variant mappings (case-insensitive)
            else:
                lc = col.lower()
                if "lease_commence" in lc or (("lease" in lc or "commencement" in lc) and "year" in lc):
                    val = lease_start
                elif "remaining_lease" in lc:
                    val = remaining_lease
                elif "storey_mid" in lc or ("storey" in lc and "mid" in lc):
                    val = storey_mid
                elif lc == "txn_year" or "transaction_year" in lc:
                    val = txn_year
                elif lc == "txn_month" or "transaction_month" in lc:
                    val = txn_month
                elif lc == "txn_quarter" or "transaction_quarter" in lc:
                    val = txn_quarter
                elif "lease_end" in lc:
                    val = lease_end_year
                elif "flat_age" in lc or "age_at_txn" in lc:
                    val = flat_age_at_txn
                else:
                    # fallback: use from original payload if present (but skip DROP_COLS)
                    if col not in DROP_COLS:
                        val = features.get(col)
            
            normalized[col] = val

        return normalized

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.model or not self.preprocessor:
            raise RuntimeError("AVM model not loaded")
        if not self.feature_columns:
            raise RuntimeError("Feature columns not defined")
        
        # Build X in correct column order
        X_dict = {c: features.get(c, None) for c in self.feature_columns}
        # Preprocess - prefer DataFrame with named columns (safer for ColumnTransformer)
        try:
            import pandas as pd

            df = pd.DataFrame([X_dict], columns=self.feature_columns)
            X = self.preprocessor.transform(df)
        except Exception as e:
            # fallback to list-form
            try:
                X = self.preprocessor.transform([list(X_dict.values())])
            except Exception as e2:
                raise RuntimeError(f"Preprocessing failed: {e}; fallback failed: {e2}") from e2

        try:
            y_pred_log = self.model.predict(X)
        except Exception as e:
            raise RuntimeError(f"Model prediction failed: {e}") from e

        # Model was trained on log-transformed prices; convert back
        pred_log = float(y_pred_log[0])
        pred = float(np.expm1(pred_log))  # inverse of log1p, ensure native float
        
        out = {"predicted_price": pred}
        if "residual_std" in self.metadata:
            std = float(self.metadata["residual_std"])
            out["confidence_interval"] = [pred - 1.96 * std, pred + 1.96 * std]
        return out

    def batch_predict(self, payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for p in payloads:
            feats = self.featurize(p)
            results.append(self.predict(feats))
        return results

    def predict_with_explanation(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict price and return SHAP-based explanation."""
        if not self.model or not self.preprocessor:
            raise RuntimeError("AVM model not loaded")
        
        # Get base prediction
        base_result = self.predict(features)
        predicted_price_sgd = base_result["predicted_price"]
        
        explanation = None
        if self._shap_explainer and SHAP_AVAILABLE:
            try:
                # Build X in correct column order (same as predict)
                X_dict = {c: features.get(c, None) for c in self.feature_columns}
                import pandas as pd
                df = pd.DataFrame([X_dict], columns=self.feature_columns)
                X_preprocessed = self.preprocessor.transform(df)
                
                # Get SHAP values (these are in log-transformed price space)
                shap_values = self._shap_explainer.shap_values(X_preprocessed)
                
                # Handle dense/sparse array formats
                if hasattr(shap_values, 'toarray'):
                    shap_values = shap_values.toarray()[0]
                else:
                    shap_values = np.array(shap_values).flatten()[:len(self.feature_columns)]
                
                # Get feature values from preprocessed X
                if hasattr(X_preprocessed, 'toarray'):
                    feat_vals = X_preprocessed.toarray()[0]
                else:
                    feat_vals = np.array(X_preprocessed).flatten()[:len(self.feature_columns)]
                
                # Get base value from explainer (in log-transformed space)
                base_value_log = float(self._shap_explainer.expected_value) if hasattr(self._shap_explainer, 'expected_value') else 0.0
                base_price_log = base_value_log
                
                # Convert from log space to SGD
                base_price_sgd_calc = float(np.expm1(base_price_log))
                
                # IMPORTANT: SHAP values are in log(price) space, not SGD space.
                # To convert to SGD impact, we scale by the model's output at that point.
                # Using: SGD_impact ≈ shap_value_log * predicted_price
                scale_factor = predicted_price_sgd / (1 + predicted_price_sgd / 100000)  # Rough scale adjustment
                
                # Build explanation dict
                contributions = []
                for fname, shap_val_log, feat_val in zip(self.feature_columns, shap_values, feat_vals):
                    # Convert log-space contribution to approximate SGD impact
                    # Rough approximation: log contribution * price / ln(price)
                    if predicted_price_sgd > 0:
                        sgd_contribution = float(shap_val_log * predicted_price_sgd)
                    else:
                        sgd_contribution = 0.0
                    
                    contributions.append({
                        "feature_name": fname,
                        "contribution": sgd_contribution,  # Now in SGD, not log space
                        "feature_value": float(feat_val),
                    })
                
                # Sort by absolute contribution
                contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
                
                explanation = {
                    "base_price": base_price_sgd_calc,
                    "feature_contributions": contributions[:10],  # Top 10 features
                    "top_contributors": [c["feature_name"] for c in contributions[:5]],
                }
            except Exception as e:
                logger.warning(f"SHAP explanation failed: {e}")
        
        result = {
            "predicted_price": predicted_price_sgd,
            "confidence_lower": base_result.get("confidence_interval", [predicted_price_sgd * 0.92, predicted_price_sgd * 1.08])[0],
            "confidence_upper": base_result.get("confidence_interval", [predicted_price_sgd * 0.92, predicted_price_sgd * 1.08])[1],
            "explanation": explanation,
        }
        
        return result

