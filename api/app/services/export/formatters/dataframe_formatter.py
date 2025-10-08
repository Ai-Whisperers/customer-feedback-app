"""DataFrame formatters for export service."""

from typing import Dict, Any, List
import pandas as pd


class DataFrameFormatter:
    """Creates DataFrames from analysis results."""

    @staticmethod
    def create_summary_dataframe(results: Dict[str, Any]) -> pd.DataFrame:
        """
        Create summary DataFrame with key metrics.

        Args:
            results: Analysis results dictionary

        Returns:
            DataFrame with two columns: Métrica and Valor
        """
        summary = results.get("summary", {})
        nps_data = summary.get("nps", {})
        churn_data = summary.get("churn_risk", {})
        metadata = results.get("metadata", {})

        summary_data = {
            "Métrica": [
                "NPS Score",
                "Total Comentarios",
                "Promotores",
                "Pasivos",
                "Detractores",
                "Riesgo Promedio (%)",
                "Alto Riesgo",
                "Tiempo Procesamiento (s)"
            ],
            "Valor": [
                round(nps_data.get("score", 0), 1),
                metadata.get("total_comments", 0),
                f"{nps_data.get('promoters', 0)} ({round(nps_data.get('promoters_percentage', 0), 1)}%)",
                f"{nps_data.get('passives', 0)} ({round(nps_data.get('passives_percentage', 0), 1)}%)",
                f"{nps_data.get('detractors', 0)} ({round(nps_data.get('detractors_percentage', 0), 1)}%)",
                round(churn_data.get("average", 0) * 100, 1),
                f"{churn_data.get('high_risk_count', 0)} ({round(churn_data.get('high_risk_percentage', 0), 1)}%)",
                round(metadata.get("processing_time_seconds", 0), 1)
            ]
        }

        return pd.DataFrame(summary_data)

    @staticmethod
    def create_detailed_dataframe(rows_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create detailed DataFrame with per-row analysis.

        Args:
            rows_data: List of row dictionaries from analysis results

        Returns:
            DataFrame with columns for each analysis field
        """
        detailed_data = []

        for row in rows_data:
            row_data = {
                "Index": row.get("index", 0) + 1,  # 1-based index for display
                "Comentario": row.get("original_text", ""),
                "Nota": row.get("nota", 5),
                "Categoría NPS": row.get("nps_category", "passive"),
                "Sentimiento": row.get("sentiment", "neutral"),
                "Idioma": row.get("language", "es"),
                "Riesgo de Abandono (%)": round(row.get("churn_risk", 0.5) * 100, 1),
                "Puntos de Dolor": "; ".join(row.get("pain_points", [])) if row.get("pain_points") else "N/A"
            }

            # Add top emotions (above 0.3 threshold)
            emotions = row.get("emotions", {})
            if emotions:
                top_emotions = [
                    f"{emotion}: {round(score * 100, 1)}%"
                    for emotion, score in emotions.items()
                    if isinstance(score, (int, float)) and score > 0.3
                ]
                row_data["Emociones Principales"] = "; ".join(top_emotions) if top_emotions else "N/A"
            else:
                row_data["Emociones Principales"] = "N/A"

            detailed_data.append(row_data)

        return pd.DataFrame(detailed_data)

    @staticmethod
    def create_emotions_dataframe(rows_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create DataFrame with emotion scores for each row.

        Args:
            rows_data: List of row dictionaries

        Returns:
            DataFrame with Index and all emotion columns
        """
        emotions_data = []

        # Collect all unique emotions
        all_emotions = set()
        for row in rows_data:
            emotions = row.get("emotions", {})
            all_emotions.update(emotions.keys())

        # Sort emotions alphabetically
        emotion_columns = sorted(all_emotions)

        for row in rows_data:
            row_emotions = {"Index": row.get("index", 0) + 1}
            emotions = row.get("emotions", {})

            for emotion in emotion_columns:
                score = emotions.get(emotion, 0)
                row_emotions[emotion.capitalize()] = round(score * 100, 1)  # Convert to percentage

            emotions_data.append(row_emotions)

        return pd.DataFrame(emotions_data)

    @staticmethod
    def create_pain_points_dataframe(results: Dict[str, Any]) -> pd.DataFrame:
        """
        Create DataFrame with pain points summary.

        Args:
            results: Analysis results dictionary

        Returns:
            DataFrame with pain points and their frequencies
        """
        summary = results.get("summary", {})
        pain_points = summary.get("pain_points", [])

        if not pain_points:
            return pd.DataFrame({"Punto de Dolor": ["Sin datos"], "Frecuencia": [0], "Porcentaje": ["0%"]})

        pain_data = []
        for pain in pain_points:
            pain_data.append({
                "Punto de Dolor": pain.get("category", "Unknown"),
                "Frecuencia": pain.get("count", 0),
                "Porcentaje": f"{round(pain.get('percentage', 0), 1)}%"
            })

        return pd.DataFrame(pain_data)
