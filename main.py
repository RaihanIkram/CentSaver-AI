
import json
from pathlib import Path
from datetime import date

import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from fastapi import FastAPI
from pydantic import BaseModel

ARTIFACT_DIR = Path("artifacts_centsaver")


class SpendingAttentionBlock(layers.Layer):
    def __init__(self, units=64, **kwargs):
        super().__init__(**kwargs)
        self.units = units
        self.gate_dense = layers.Dense(units, activation="sigmoid")
        self.value_dense = layers.Dense(units, activation="tanh")
        self.out_dense = layers.Dense(units, activation="relu")

    def call(self, inputs):
        gate = self.gate_dense(inputs)
        value = self.value_dense(inputs)
        return self.out_dense(gate * value)

    def get_config(self):
        config = super().get_config()
        config.update({"units": self.units})
        return config


class AdaptiveFocalLoss(keras.losses.Loss):
    def __init__(self, gamma=2.0, alpha=0.35, name="adaptive_focal_loss"):
        super().__init__(name=name)
        self.gamma = gamma
        self.alpha = alpha

    def call(self, y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        y_pred = tf.clip_by_value(tf.cast(y_pred, tf.float32), 1e-7, 1.0 - 1e-7)
        bce = -(y_true * tf.math.log(y_pred) + (1.0 - y_true) * tf.math.log(1.0 - y_pred))
        p_t = y_true * y_pred + (1.0 - y_true) * (1.0 - y_pred)
        alpha_factor = y_true * self.alpha + (1.0 - y_true) * (1.0 - self.alpha)
        modulating_factor = tf.pow(1.0 - p_t, self.gamma)
        return tf.reduce_mean(alpha_factor * modulating_factor * bce)

    def get_config(self):
        return {"gamma": self.gamma, "alpha": self.alpha, "name": self.name}


with open(ARTIFACT_DIR / "model_config.json", encoding="utf-8") as f:
    CONFIG = json.load(f)

NUMERIC_FEATURES = CONFIG["numeric_features"]
BEST_THRESHOLD = float(CONFIG["best_threshold"])
BEST_MICRO_THRESHOLD = float(CONFIG.get("best_micro_threshold", 0.5))

MODEL = keras.models.load_model(
    ARTIFACT_DIR / CONFIG.get("classification_model_path", CONFIG["model_path"]),
    custom_objects={
        "SpendingAttentionBlock": SpendingAttentionBlock,
        "AdaptiveFocalLoss": AdaptiveFocalLoss,
    },
    compile=False,
)

SCALER = joblib.load(ARTIFACT_DIR / CONFIG["scaler_path"])

with open(ARTIFACT_DIR / CONFIG["category_to_index_path"], encoding="utf-8") as f:
    CATEGORY_TO_INDEX = json.load(f)

BASELINE = pd.read_csv(ARTIFACT_DIR / CONFIG["baseline_path"])
FREQUENCY = pd.read_csv(ARTIFACT_DIR / CONFIG.get("frequency_baseline_path", "category_frequency_baseline.csv"))

REGRESSION_MODEL = None
REGRESSION_SCALER = None
REGRESSION_FEATURES = []
MONTHLY_HISTORY = None

if "regression_model_path" in CONFIG:
    REGRESSION_MODEL = keras.models.load_model(
        ARTIFACT_DIR / CONFIG["regression_model_path"],
        custom_objects={"SpendingAttentionBlock": SpendingAttentionBlock},
        compile=False,
    )
    REGRESSION_SCALER = joblib.load(ARTIFACT_DIR / CONFIG["regression_scaler_path"])
    with open(ARTIFACT_DIR / CONFIG["regression_numeric_features_path"], encoding="utf-8") as f:
        REGRESSION_FEATURES = json.load(f)
    MONTHLY_HISTORY = pd.read_csv(ARTIFACT_DIR / CONFIG["monthly_regression_history_path"])
    MONTHLY_HISTORY["period"] = pd.to_datetime(MONTHLY_HISTORY["period"])


baseline_fallback = {
    "cat_day_avg": BASELINE["cat_day_avg"].mean(),
    "cat_day_median": BASELINE["cat_day_median"].median(),
    "cat_day_std": BASELINE["cat_day_std"].mean(),
    "cat_day_q25": BASELINE["cat_day_q25"].median(),
    "cat_day_q75": BASELINE["cat_day_q75"].median(),
    "cat_day_q90": BASELINE["cat_day_q90"].median(),
    "cat_day_count": BASELINE["cat_day_count"].median(),
}

frequency_fallback = {
    "monthly_category_txn_count_avg": FREQUENCY["monthly_category_txn_count_avg"].mean(),
    "monthly_category_txn_count_median": FREQUENCY["monthly_category_txn_count_median"].median(),
    "monthly_category_txn_count_max": FREQUENCY["monthly_category_txn_count_max"].max(),
}


class TransactionRequest(BaseModel):
    amount: float
    category: str
    transaction_date: date


class MonthlyAlertRequest(BaseModel):
    month: int
    year: int
    top_n: int = 8


app = FastAPI(title="CentSaver Classification + Regression API")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "classification_model": CONFIG.get("classification_model_path", CONFIG["model_path"]),
        "regression_model": CONFIG.get("regression_model_path"),
    }


def get_baseline(category, day_type):
    row = BASELINE[(BASELINE["category"] == category) & (BASELINE["day_type"] == day_type)]
    if len(row) == 0:
        return baseline_fallback.copy()
    return row.iloc[0].to_dict()


def get_frequency(category):
    row = FREQUENCY[FREQUENCY["category"] == category]
    if len(row) == 0:
        return frequency_fallback.copy()
    return row.iloc[0].to_dict()


def build_transaction_row(amount, category, transaction_date):
    dt = pd.to_datetime(transaction_date)
    day_of_week = int(dt.dayofweek)
    is_weekend = int(day_of_week in [5, 6])
    day_type = "weekend" if is_weekend else "weekday"
    base = get_baseline(category, day_type)
    freq = get_frequency(category)

    cat_avg = float(base["cat_day_avg"])
    cat_std = float(base["cat_day_std"] or baseline_fallback["cat_day_std"])
    amount_ratio = amount / cat_avg if cat_avg > 0 else 1.0
    amount_zscore = (amount - cat_avg) / cat_std if cat_std > 0 else 0.0

    small_amount_flag = int(
        (float(amount) <= float(base["cat_day_q25"])) and
        (float(amount) <= float(base["cat_day_median"]))
    )
    repetitive_category_flag = int(
        float(freq["monthly_category_txn_count_avg"]) >= float(frequency_fallback["monthly_category_txn_count_median"])
    )

    row = pd.DataFrame([{
        "amount": float(amount),
        "amount_log": float(np.log1p(amount)),
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "month": int(dt.month),
        "year": int(dt.year),
        "cat_day_avg": cat_avg,
        "cat_day_median": float(base["cat_day_median"]),
        "cat_day_std": cat_std,
        "cat_day_q25": float(base["cat_day_q25"]),
        "cat_day_q75": float(base["cat_day_q75"]),
        "cat_day_q90": float(base["cat_day_q90"]),
        "cat_day_count": float(base["cat_day_count"]),
        "amount_ratio": amount_ratio,
        "amount_zscore": amount_zscore,
        "monthly_category_txn_count_avg": float(freq["monthly_category_txn_count_avg"]),
        "monthly_category_txn_count_median": float(freq["monthly_category_txn_count_median"]),
        "monthly_category_txn_count_max": float(freq["monthly_category_txn_count_max"]),
        "small_amount_flag": small_amount_flag,
        "repetitive_category_flag": repetitive_category_flag,
    }])[NUMERIC_FEATURES]
    return row, amount_ratio, amount_zscore


@app.post("/predict-transaction")
def predict_transaction(req: TransactionRequest):
    row, amount_ratio, amount_zscore = build_transaction_row(req.amount, req.category, req.transaction_date)
    x_num = SCALER.transform(row)
    x_cat = np.array([[int(CATEGORY_TO_INDEX.get(req.category, 0))]])
    pred = MODEL.predict({"numeric_input": x_num, "category_input": x_cat}, verbose=0)
    risk_prob = float(pred["risk_output"].reshape(-1)[0])
    micro_prob = float(pred["micro_output"].reshape(-1)[0])
    return {
        "category": req.category,
        "amount": req.amount,
        "risk_probability": round(risk_prob, 4),
        "risk_label": int(risk_prob >= BEST_THRESHOLD),
        "micro_probability": round(micro_prob, 4),
        "micro_label": int(micro_prob >= BEST_MICRO_THRESHOLD),
        "amount_ratio_vs_category_avg": round(amount_ratio, 3),
        "amount_zscore_vs_category": round(amount_zscore, 3),
    }


def normalize_month_start(year, month):
    return pd.Timestamp(year=int(year), month=int(month), day=1)


def build_regression_feature_for_target(monthly_hist, category, target_period):
    target_period = pd.to_datetime(target_period).to_period("M").to_timestamp()
    cat_hist = monthly_hist[
        (monthly_hist["category"] == category) &
        (monthly_hist["period"] < target_period)
    ].sort_values("period")

    if cat_hist.empty:
        last_total = rolling3_total = rolling6_total = same_month_avg = 0.0
        last_txn_count = rolling3_txn_count = rolling6_txn_count = 0.0
        last_avg_amount = 0.0
        last_risk_rate = rolling3_risk_rate = 0.0
        last_micro_rate = rolling3_micro_rate = 0.0
    else:
        last_row = cat_hist.iloc[-1]
        last_total = float(last_row["total_amount"])
        rolling3_total = float(cat_hist.tail(3)["total_amount"].mean())
        rolling6_total = float(cat_hist.tail(6)["total_amount"].mean())
        same_month_hist = cat_hist[cat_hist["period"].dt.month == target_period.month]
        same_month_avg = float(same_month_hist["total_amount"].mean()) if len(same_month_hist) else rolling6_total
        last_txn_count = float(last_row["txn_count"])
        rolling3_txn_count = float(cat_hist.tail(3)["txn_count"].mean())
        rolling6_txn_count = float(cat_hist.tail(6)["txn_count"].mean())
        last_avg_amount = float(last_row["avg_amount"])
        last_risk_rate = float(last_row["risk_rate"])
        rolling3_risk_rate = float(cat_hist.tail(3)["risk_rate"].mean())
        last_micro_rate = float(last_row["micro_rate"])
        rolling3_micro_rate = float(cat_hist.tail(3)["micro_rate"].mean())

    month = int(target_period.month)
    year = int(target_period.year)

    return {
        "target_month": month,
        "target_year": year,
        "target_month_sin": float(np.sin(2 * np.pi * month / 12)),
        "target_month_cos": float(np.cos(2 * np.pi * month / 12)),
        "last_month_total": last_total,
        "last_month_total_log": float(np.log1p(last_total)),
        "rolling3_total": rolling3_total,
        "rolling6_total": rolling6_total,
        "same_month_avg": same_month_avg,
        "last_month_txn_count": last_txn_count,
        "rolling3_txn_count": rolling3_txn_count,
        "rolling6_txn_count": rolling6_txn_count,
        "last_month_avg_amount": last_avg_amount,
        "last_month_risk_rate": last_risk_rate,
        "rolling3_risk_rate": rolling3_risk_rate,
        "last_month_micro_rate": last_micro_rate,
        "rolling3_micro_rate": rolling3_micro_rate,
    }


def classify_status(growth_ratio, risk_probability, micro_probability):
    if risk_probability >= 0.75:
        return "HIGH", "risk_probability"
    if growth_ratio >= 1.35:
        return "HIGH", "growth_ratio"
    if micro_probability >= 0.70:
        return "WARNING", "micro_probability"
    if risk_probability >= 0.55:
        return "WARNING", "risk_probability"
    if growth_ratio >= 1.15:
        return "WARNING", "growth_ratio"
    return "NORMAL", "normal"


@app.post("/monthly-alert")
def monthly_alert(req: MonthlyAlertRequest):
    if REGRESSION_MODEL is None or MONTHLY_HISTORY is None:
        return {"error": "Regression artifacts are not available."}

    target_period = normalize_month_start(req.year, req.month)
    categories = sorted(MONTHLY_HISTORY["category"].dropna().unique().tolist())
    rows = []

    for category in categories:
        feature = build_regression_feature_for_target(MONTHLY_HISTORY, category, target_period)
        feature_df = pd.DataFrame([feature])[REGRESSION_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
        x_num = REGRESSION_SCALER.transform(feature_df)
        x_cat = np.array([[int(CATEGORY_TO_INDEX.get(category, 0))]])
        pred_log = REGRESSION_MODEL.predict(
            {"reg_numeric_input": x_num, "reg_category_input": x_cat},
            verbose=0,
        ).reshape(-1)[0]
        forecast_total = max(float(np.expm1(pred_log)), 0.0)

        hist = MONTHLY_HISTORY[
            (MONTHLY_HISTORY["category"] == category) &
            (MONTHLY_HISTORY["period"] < target_period)
        ].sort_values("period")

        if len(hist):
            same_month_hist = hist[hist["period"].dt.month == target_period.month]
            if len(same_month_hist):
                historical_reference = float(same_month_hist["total_amount"].mean())
                expected_txn_count = int(round(same_month_hist["txn_count"].mean()))
                baseline_method = "same_month_historical_average"
            else:
                historical_reference = float(hist["total_amount"].mean())
                expected_txn_count = int(round(hist["txn_count"].mean()))
                baseline_method = "category_average_fallback_no_same_month_history"
        else:
            historical_reference = max(forecast_total, 1.0)
            expected_txn_count = 1
            baseline_method = "forecast_fallback_no_history"

        expected_txn_count = max(expected_txn_count, 1)
        growth_ratio = forecast_total / max(historical_reference, 1.0)

        estimated_avg_txn = max(forecast_total / expected_txn_count, 1.0)
        tx_row, _, _ = build_transaction_row(estimated_avg_txn, category, target_period)
        tx_num = SCALER.transform(tx_row)
        tx_cat = np.array([[int(CATEGORY_TO_INDEX.get(category, 0))]])
        tx_pred = MODEL.predict({"numeric_input": tx_num, "category_input": tx_cat}, verbose=0)
        risk_probability = float(tx_pred["risk_output"].reshape(-1)[0])
        micro_probability = float(tx_pred["micro_output"].reshape(-1)[0])
        status, trigger = classify_status(growth_ratio, risk_probability, micro_probability)

        rows.append({
            "month": int(target_period.month),
            "period": target_period.strftime("%Y-%m"),
            "category": category,
            "forecast_total": round(forecast_total, 2),
            "historical_reference": round(max(float(historical_reference), 1.0), 2),
            "baseline_method": baseline_method,
            "growth_ratio": round(growth_ratio, 4),
            "risk_probability": round(risk_probability, 4),
            "micro_probability": round(micro_probability, 4),
            "trigger": trigger,
            "status": status,
            "forecast_method": "TensorFlow Regression",
        })

    status_rank = {"HIGH": 0, "WARNING": 1, "NORMAL": 2}
    rows = sorted(rows, key=lambda item: (status_rank.get(item["status"], 9), -item["forecast_total"]))
    return {
        "month": int(target_period.month),
        "period": target_period.strftime("%Y-%m"),
        "total_categories": len(rows),
        "items": rows[: max(int(req.top_n), 1)],
    }
