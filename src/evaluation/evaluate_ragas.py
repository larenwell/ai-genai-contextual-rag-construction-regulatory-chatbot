#!/usr/bin/env python3
"""
Evaluación RAG con RAGAS - Script Principal
==========================================

Este script implementa una evaluación completa del sistema RAG utilizando RAGAS.
Evalúa 64 preguntas de diferentes tipos contra la API existente en api_rag.py.

Funcionalidades:
- Carga dataset desde JSON Lines
- Cliente HTTP para llamar a api_rag.py
- Configuración RAGAS con Mistral como LLM evaluador
- Procesamiento por batches de las 64 preguntas
- Cálculo de métricas: faithfulness, answer_relevancy, context_precision, context_recall
- Generación de reporte completo con análisis por tipo de pregunta
- Exportar resultados a CSV/JSON

Autor: Laren Osorio Toribio
Fecha: 2025-09-05
"""

import os
import sys
import json
import time
import math
import logging
import requests
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

# Agregar directorio global para langchain_mistralai
sys.path.append('/usr/local/lib/python3.12/dist-packages')

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / '.env')

# RAGAS imports
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    answer_correctness
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from datasets import Dataset

# LangChain imports for Mistral
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings as LangChainOllamaEmbeddings
from langchain_mistralai import ChatMistralAI as LangChainMistralAI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation_ragas.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    """Estructura para almacenar resultados de evaluación"""
    question: str
    answer: str
    ground_truth: str
    context: List[str]
    question_type: str
    faithfulness_score: float
    answer_relevancy_score: float
    context_precision_score: float
    context_recall_score: float
    answer_correctness_score: float
    api_response_time: float
    evaluation_time: float
    context_sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

class RAGEvaluator:
    """
    Evaluador principal del sistema RAG usando RAGAS.
    
    Esta clase maneja toda la evaluación del sistema RAG, incluyendo:
    - Comunicación con la API existente
    - Configuración de RAGAS con Mistral
    - Procesamiento de preguntas en batches
    - Cálculo de métricas de evaluación
    - Generación de reportes
    """
    
    def __init__(self, api_url: str = "http://localhost:8001", dataset_path: str = None):
        """
        Inicializa el evaluador RAG.
        
        Args:
            api_url: URL de la API RAG existente
            dataset_path: Ruta al dataset de evaluación
        """
        self.api_url = api_url
        self.dataset_path = dataset_path or Path(__file__).parent / "data" / "evaluation_dataset.jsonl"
        self.results: List[EvaluationResult] = []
        
        # Configurar Mistral para RAGAS
        self._setup_mistral_for_ragas()
        
        # Configurar métricas RAGAS
        self._setup_ragas_metrics()
        
        logger.info("RAGEvaluator inicializado correctamente")
    
    def _setup_mistral_for_ragas(self):
        """Configura Mistral como LLM evaluador para RAGAS"""
        try:
            # Configurar Mistral usando LangChain
            mistral_langchain = LangChainMistralAI(
                api_key=os.getenv("MISTRAL_API_KEY"),
                model="mistral-large-latest"
            )
            
            # Envolver con LangchainLLMWrapper para RAGAS
            self.mistral_llm = LangchainLLMWrapper(mistral_langchain)
            
            # Configurar embeddings de Ollama usando LangChain
            ollama_langchain = LangChainOllamaEmbeddings(
                model="nomic-embed-text",
                base_url="http://localhost:11434"
            )
            
            # Envolver con LangchainEmbeddingsWrapper para RAGAS
            self.ollama_embeddings = LangchainEmbeddingsWrapper(ollama_langchain)
            
            logger.info("Mistral configurado correctamente para RAGAS")
            
        except Exception as e:
            logger.error(f"Error configurando Mistral para RAGAS: {e}")
            raise
    
    def _setup_ragas_metrics(self):
        """Configura las métricas RAGAS a utilizar"""
        self.metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
            answer_correctness
        ]
        logger.info("Métricas RAGAS configuradas: faithfulness, answer_relevancy, context_precision, context_recall, answer_correctness")
    
    def load_dataset(self) -> List[Dict[str, Any]]:
        """
        Carga el dataset de evaluación desde JSON Lines.
        
        Returns:
            Lista de diccionarios con las preguntas de evaluación
        """
        try:
            dataset = []
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            dataset.append(data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Error en línea {line_num}: {e}")
                            continue
            
            logger.info(f"Dataset cargado: {len(dataset)} preguntas")
            return dataset
            
        except FileNotFoundError:
            logger.error(f"Dataset no encontrado: {self.dataset_path}")
            raise
        except Exception as e:
            logger.error(f"Error cargando dataset: {e}")
            raise
    
    def check_api_availability(self) -> bool:
        """
        Verifica que la API RAG esté disponible.
        
        Returns:
            True si la API está disponible, False en caso contrario
        """
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=5)
            if response.status_code == 200:
                logger.info("API RAG está disponible")
                return True
            else:
                logger.warning(f"API respondió con código {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"API no disponible: {e}")
            return False
    
    def query_rag_api(self, question: str) -> Dict[str, Any]:
        """
        Realiza una consulta a la API RAG existente.
        
        Args:
            question: Pregunta a consultar
            
        Returns:
            Respuesta de la API con answer, context, etc.
        """
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}/rag",
                json={"question": question},
                timeout=30
            )
            
            api_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Asegurar que context y context_sources sean listas
                context = data.get("context", data.get("relevant_docs", []))
                context_sources = data.get("context_sources", [])
                
                # Si context es string, intentar parsearlo como JSON
                if isinstance(context, str):
                    try:
                        context = json.loads(context)
                    except:
                        context = [context]  # Si no se puede parsear, convertir a lista
                
                # Si context_sources es string, intentar parsearlo como JSON
                if isinstance(context_sources, str):
                    try:
                        context_sources = json.loads(context_sources)
                    except:
                        context_sources = [context_sources]  # Si no se puede parsear, convertir a lista
                
                return {
                    "answer": data.get("answer", ""),
                    "context": context,
                    "context_sources": context_sources,
                    "workflow_info": data.get("workflow_info", {}),
                    "api_time": api_time,
                    "success": True
                }
            else:
                logger.error(f"API error {response.status_code}: {response.text}")
                return {
                    "answer": "",
                    "context": [],
                    "context_sources": [],
                    "workflow_info": {},
                    "api_time": api_time,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            logger.error("Timeout en consulta API")
            return {
                "answer": "",
                "context": [],
                "context_sources": [],
                "workflow_info": {},
                "api_time": 30.0,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Error en consulta API: {e}")
            return {
                "answer": "",
                "context": [],
                "context_sources": [],
                "workflow_info": {},
                "api_time": 0.0,
                "success": False,
                "error": str(e)
            }
    
    def evaluate_single_question(self, question_data: Dict[str, Any]) -> EvaluationResult:
        """
        Evalúa una sola pregunta usando RAGAS.
        
        Args:
            question_data: Datos de la pregunta del dataset
            
        Returns:
            Resultado de la evaluación
        """
        question = question_data["question"]
        ground_truth = question_data["ground_truth"]
        question_type = question_data["question_type"]
        
        logger.info(f"Evaluando pregunta tipo '{question_type}': {question[:50]}...")
        
        # Consultar API RAG
        api_response = self.query_rag_api(question)
        
        if not api_response["success"]:
            return EvaluationResult(
                question=question,
                answer="",
                ground_truth=ground_truth,
                context=[],
                context_sources=[],
                question_type=question_type,
                faithfulness_score=0.0,
                answer_relevancy_score=0.0,
                context_precision_score=0.0,
                context_recall_score=0.0,
                answer_correctness_score=0.0,
                api_response_time=api_response["api_time"],
                evaluation_time=0.0,
                error=api_response.get("error", "API Error")
            )
        
        # Preparar datos para RAGAS
        ragas_data = {
            "question": [question],
            "answer": [api_response["answer"]],
            "ground_truth": [ground_truth],
            "contexts": [api_response.get("context", api_response.get("relevant_docs", []))]
        }
        
        try:
            # Evaluar con RAGAS
            eval_start = time.time()
            
            # Crear Dataset de Hugging Face para RAGAS 0.3.2
            dataset = Dataset.from_dict(ragas_data)
            
            # Ejecutar evaluación
            result = evaluate(
                dataset,
                metrics=self.metrics,
                llm=self.mistral_llm,
                embeddings=self.ollama_embeddings,
                show_progress=False
            )
            
            eval_time = time.time() - eval_start
            
            # Extraer scores del resultado
            scores_raw = result.scores if hasattr(result, 'scores') else {}
            
            # RAGAS devuelve una lista de diccionarios, necesitamos el primer elemento
            if isinstance(scores_raw, list) and len(scores_raw) > 0:
                scores = scores_raw[0]
            elif isinstance(scores_raw, dict):
                scores = scores_raw
            else:
                scores = {}
            
            logger.info(f"Scores extraídos: {scores}")
            logger.info(f"Tipo de scores: {type(scores)}")
            
            return EvaluationResult(
                question=question,
                answer=api_response["answer"],
                ground_truth=ground_truth,
                context=api_response["context"],
                context_sources=api_response.get("context_sources", []),
                question_type=question_type,
                faithfulness_score=scores.get("faithfulness", 0.0) if isinstance(scores, dict) else 0.0,
                answer_relevancy_score=scores.get("answer_relevancy", 0.0) if isinstance(scores, dict) else 0.0,
                context_precision_score=scores.get("context_precision", 0.0) if isinstance(scores, dict) else 0.0,
                context_recall_score=scores.get("context_recall", 0.0) if isinstance(scores, dict) else 0.0,
                answer_correctness_score=scores.get("answer_correctness", 0.0) if isinstance(scores, dict) else 0.0,
                api_response_time=api_response["api_time"],
                evaluation_time=eval_time
            )
            
        except Exception as e:
            logger.error(f"Error en evaluación RAGAS: {e}")
            return EvaluationResult(
                question=question,
                answer=api_response["answer"],
                ground_truth=ground_truth,
                context=api_response["context"],
                context_sources=api_response.get("context_sources", []),
                question_type=question_type,
                faithfulness_score=0.0,
                answer_relevancy_score=0.0,
                context_precision_score=0.0,
                context_recall_score=0.0,
                answer_correctness_score=0.0,
                api_response_time=api_response["api_time"],
                evaluation_time=0.0,
                error=str(e)
            )
    
    def evaluate_batch(self, questions: List[Dict[str, Any]], batch_size: int = 5) -> List[EvaluationResult]:
        """
        Evalúa un lote de preguntas.
        
        Args:
            questions: Lista de preguntas a evaluar
            batch_size: Tamaño del lote
            
        Returns:
            Lista de resultados de evaluación
        """
        results = []
        total_questions = len(questions)
        
        logger.info(f"Evaluando lote de {total_questions} preguntas en grupos de {batch_size}")
        
        for i in range(0, total_questions, batch_size):
            batch = questions[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_questions + batch_size - 1) // batch_size
            
            logger.info(f"Procesando lote {batch_num}/{total_batches} ({len(batch)} preguntas)")
            
            for question_data in batch:
                try:
                    result = self.evaluate_single_question(question_data)
                    results.append(result)
                    
                    # Pequeña pausa entre preguntas para no sobrecargar la API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error procesando pregunta: {e}")
                    # Crear resultado de error
                    error_result = EvaluationResult(
                        question=question_data["question"],
                        answer="",
                        ground_truth=question_data["ground_truth"],
                        context=[],
                        context_sources=[],
                        question_type=question_data["question_type"],
                        faithfulness_score=0.0,
                        answer_relevancy_score=0.0,
                        context_precision_score=0.0,
                        context_recall_score=0.0,
                        answer_correctness_score=0.0,
                        api_response_time=0.0,
                        evaluation_time=0.0,
                        error=str(e)
                    )
                    results.append(error_result)
        
        return results
    
    def calculate_metrics_by_type(self) -> Dict[str, Dict[str, float]]:
        """
        Calcula métricas agrupadas por tipo de pregunta.
        
        Returns:
            Diccionario con métricas por tipo
        """
        type_metrics = {}
        
        for result in self.results:
            if result.error:
                continue
                
            question_type = result.question_type
            
            if question_type not in type_metrics:
                type_metrics[question_type] = {
                    "faithfulness": [],
                    "answer_relevancy": [],
                    "context_precision": [],
                    "context_recall": [],
                    "answer_correctness": [],
                    "api_response_time": [],
                    "evaluation_time": []
                }
            
            type_metrics[question_type]["faithfulness"].append(result.faithfulness_score)
            type_metrics[question_type]["answer_relevancy"].append(result.answer_relevancy_score)
            type_metrics[question_type]["context_precision"].append(result.context_precision_score)
            type_metrics[question_type]["context_recall"].append(result.context_recall_score)
            type_metrics[question_type]["answer_correctness"].append(result.answer_correctness_score)
            type_metrics[question_type]["api_response_time"].append(result.api_response_time)
            type_metrics[question_type]["evaluation_time"].append(result.evaluation_time)
        
        # Calcular promedios
        for question_type in type_metrics:
            metrics = type_metrics[question_type]
            for metric_name, values in list(metrics.items()):
                if values:
                    # Filtrar valores NaN antes de calcular estadísticas
                    valid_values = [v for v in values if not math.isnan(v)]
                    
                    if valid_values:
                        type_metrics[question_type][f"{metric_name}_avg"] = sum(valid_values) / len(valid_values)
                        type_metrics[question_type][f"{metric_name}_min"] = min(valid_values)
                        type_metrics[question_type][f"{metric_name}_max"] = max(valid_values)
                    else:
                        type_metrics[question_type][f"{metric_name}_avg"] = 0.0
                        type_metrics[question_type][f"{metric_name}_min"] = 0.0
                        type_metrics[question_type][f"{metric_name}_max"] = 0.0
                else:
                    type_metrics[question_type][f"{metric_name}_avg"] = 0.0
                    type_metrics[question_type][f"{metric_name}_min"] = 0.0
                    type_metrics[question_type][f"{metric_name}_max"] = 0.0
        
        return type_metrics
    
    def generate_report(self) -> str:
        """
        Genera un reporte detallado de la evaluación.
        
        Returns:
            Reporte en formato texto
        """
        if not self.results:
            return "No hay resultados para generar reporte."
        
        # Calcular métricas generales
        total_questions = len(self.results)
        successful_evaluations = len([r for r in self.results if not r.error])
        failed_evaluations = total_questions - successful_evaluations
        
        # Métricas por tipo
        type_metrics = self.calculate_metrics_by_type()
        
        # Generar reporte
        report = []
        report.append("=" * 80)
        report.append("REPORTE DE EVALUACIÓN RAG CON RAGAS")
        report.append("=" * 80)
        report.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total de preguntas: {total_questions}")
        report.append(f"Evaluaciones exitosas: {successful_evaluations}")
        report.append(f"Evaluaciones fallidas: {failed_evaluations}")
        report.append("")
        
        # Métricas generales
        if successful_evaluations > 0:
            # Filtrar valores válidos (no NaN) para cada métrica
            valid_faithfulness = [r.faithfulness_score for r in self.results if not r.error and not math.isnan(r.faithfulness_score)]
            valid_answer_relevancy = [r.answer_relevancy_score for r in self.results if not r.error and not math.isnan(r.answer_relevancy_score)]
            valid_context_precision = [r.context_precision_score for r in self.results if not r.error and not math.isnan(r.context_precision_score)]
            valid_context_recall = [r.context_recall_score for r in self.results if not r.error and not math.isnan(r.context_recall_score)]
            valid_answer_correctness = [r.answer_correctness_score for r in self.results if not r.error and not math.isnan(r.answer_correctness_score)]
            valid_api_times = [r.api_response_time for r in self.results if not r.error and not math.isnan(r.api_response_time)]
            
            # Calcular promedios solo con valores válidos
            avg_faithfulness = sum(valid_faithfulness) / len(valid_faithfulness) if valid_faithfulness else 0.0
            avg_answer_relevancy = sum(valid_answer_relevancy) / len(valid_answer_relevancy) if valid_answer_relevancy else 0.0
            avg_context_precision = sum(valid_context_precision) / len(valid_context_precision) if valid_context_precision else 0.0
            avg_context_recall = sum(valid_context_recall) / len(valid_context_recall) if valid_context_recall else 0.0
            avg_answer_correctness = sum(valid_answer_correctness) / len(valid_answer_correctness) if valid_answer_correctness else 0.0
            avg_api_time = sum(valid_api_times) / len(valid_api_times) if valid_api_times else 0.0
            
            report.append("MÉTRICAS GENERALES")
            report.append("-" * 40)
            report.append(f"Faithfulness (Fidelidad): {avg_faithfulness:.3f}")
            report.append(f"Answer Relevancy (Relevancia): {avg_answer_relevancy:.3f}")
            report.append(f"Context Precision (Precisión): {avg_context_precision:.3f}")
            report.append(f"Context Recall (Recuperación): {avg_context_recall:.3f}")
            report.append(f"Answer Correctness (Correctitud): {avg_answer_correctness:.3f}")
            report.append(f"Tiempo promedio API: {avg_api_time:.2f}s")
            report.append("")
        
        # Métricas por tipo de pregunta
        report.append("MÉTRICAS POR TIPO DE PREGUNTA")
        report.append("-" * 40)
        
        for question_type, metrics in type_metrics.items():
            count = len(metrics["faithfulness"])
            if count > 0:
                report.append(f"\n{question_type.upper().replace('_', ' ')} ({count} preguntas)")
                report.append(f"  Faithfulness: {metrics['faithfulness_avg']:.3f} (min: {metrics['faithfulness_min']:.3f}, max: {metrics['faithfulness_max']:.3f})")
                report.append(f"  Answer Relevancy: {metrics['answer_relevancy_avg']:.3f} (min: {metrics['answer_relevancy_min']:.3f}, max: {metrics['answer_relevancy_max']:.3f})")
                report.append(f"  Context Precision: {metrics['context_precision_avg']:.3f} (min: {metrics['context_precision_min']:.3f}, max: {metrics['context_precision_max']:.3f})")
                report.append(f"  Context Recall: {metrics['context_recall_avg']:.3f} (min: {metrics['context_recall_min']:.3f}, max: {metrics['context_recall_max']:.3f})")
                report.append(f"  Answer Correctness: {metrics['answer_correctness_avg']:.3f} (min: {metrics['answer_correctness_min']:.3f}, max: {metrics['answer_correctness_max']:.3f})")
                report.append(f"  Tiempo API promedio: {metrics['api_response_time_avg']:.2f}s")
        
        # Casos problemáticos
        report.append("\nCASOS PROBLEMÁTICOS")
        report.append("-" * 40)
        
        # Preguntas con scores bajos
        low_scores = [r for r in self.results if not r.error and r.faithfulness_score < 0.5]
        if low_scores:
            report.append(f"\nPreguntas con Faithfulness < 0.5 ({len(low_scores)} casos):")
            for result in low_scores[:5]:  # Mostrar solo los primeros 5
                report.append(f"  - {result.question[:60]}... (Score: {result.faithfulness_score:.3f})")
        
        # Errores
        if failed_evaluations > 0:
            report.append(f"\nErrores encontrados ({failed_evaluations} casos):")
            error_types = {}
            for result in self.results:
                if result.error:
                    error_type = result.error
                    error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in error_types.items():
                report.append(f"  - {error_type}: {count} casos")
        
        # Recomendaciones
        report.append("\nRECOMENDACIONES")
        report.append("-" * 40)
        
        if successful_evaluations > 0:
            if avg_faithfulness < 0.7:
                report.append("- Mejorar la fidelidad: El sistema genera respuestas que no están bien fundamentadas en el contexto")
            if avg_answer_relevancy < 0.7:
                report.append("- Mejorar la relevancia: Las respuestas no son suficientemente relevantes para las preguntas")
            if avg_context_precision < 0.7:
                report.append("- Mejorar la precisión del contexto: El sistema recupera contexto irrelevante")
            if avg_context_recall < 0.7:
                report.append("- Mejorar la recuperación: El sistema no encuentra todo el contexto relevante")
            if avg_answer_correctness < 0.7:
                report.append("- Mejorar la correctitud: Las respuestas contienen información incorrecta")
        
        if failed_evaluations > 0:
            report.append(f"- Resolver {failed_evaluations} errores de evaluación para mejorar la cobertura")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def export_results(self, output_dir: str = "evaluation_results"):
        """
        Exporta los resultados a archivos CSV y JSON.
        
        Args:
            output_dir: Directorio donde guardar los resultados
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Exportar a CSV
        csv_data = []
        for result in self.results:
            csv_data.append({
                "question": result.question,
                "answer": result.answer,
                "ground_truth": result.ground_truth,
                "question_type": result.question_type,
                "faithfulness_score": result.faithfulness_score,
                "answer_relevancy_score": result.answer_relevancy_score,
                "context_precision_score": result.context_precision_score,
                "context_recall_score": result.context_recall_score,
                "answer_correctness_score": result.answer_correctness_score,
                "api_response_time": result.api_response_time,
                "evaluation_time": result.evaluation_time,
                "context": " | ".join(result.context) if result.context else "",
                "context_sources": json.dumps(result.context_sources, ensure_ascii=False) if result.context_sources else "",
                "error": result.error or ""
            })
        
        df = pd.DataFrame(csv_data)
        csv_file = output_path / f"evaluation_results_{timestamp}.csv"
        df.to_csv(csv_file, index=False, encoding='utf-8')
        logger.info(f"Resultados exportados a CSV: {csv_file}")
        
        # Exportar a JSON
        json_data = {
            "evaluation_metadata": {
                "timestamp": timestamp,
                "total_questions": len(self.results),
                "successful_evaluations": len([r for r in self.results if not r.error]),
                "failed_evaluations": len([r for r in self.results if r.error])
            },
            "results": csv_data,
            "metrics_by_type": self.calculate_metrics_by_type()
        }
        
        json_file = output_path / f"evaluation_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            # Usar serialización JSON segura para evitar valores NaN
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=safe_json_serializer)
        logger.info(f"Resultados exportados a JSON: {json_file}")
        
        # Guardar reporte
        report_file = output_path / f"evaluation_report_{timestamp}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        logger.info(f"Reporte guardado: {report_file}")
    
    def run_evaluation(self, batch_size: int = 5):
        """
        Ejecuta la evaluación completa.
        
        Args:
            batch_size: Tamaño del lote para procesamiento
        """
        logger.info("Iniciando evaluación RAG con RAGAS")
        
        # Verificar API
        if not self.check_api_availability():
            logger.error("API no disponible. Iniciando api_rag.py...")
            logger.info("Por favor, ejecuta en otra terminal: cd src/evaluation && python api_rag.py")
            return
        
        # Cargar dataset
        try:
            dataset = self.load_dataset()
            logger.info(f"Dataset cargado: {len(dataset)} preguntas")
        except Exception as e:
            logger.error(f"Error cargando dataset: {e}")
            return
        
        # Ejecutar evaluación
        logger.info("Iniciando evaluación de preguntas...")
        self.results = self.evaluate_batch(dataset, batch_size)
        
        # Generar reporte
        logger.info("Generando reporte...")
        report = self.generate_report()
        print("\n" + report)
        
        # Exportar resultados
        logger.info("Exportando resultados...")
        self.export_results()
        
        logger.info("Evaluación completada exitosamente")

def main():
    """Función principal"""
    print("🚀 Iniciando Evaluación RAG con RAGAS")
    print("=" * 50)
    
    # Verificar variables de entorno
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY no está configurada")
        print("Por favor, configura tu API key de Mistral en el archivo .env")
        return
    
    # Crear evaluador
    evaluator = RAGEvaluator()
    
    # Ejecutar evaluación
    try:
        evaluator.run_evaluation(batch_size=3)  # Lotes pequeños para estabilidad
    except KeyboardInterrupt:
        print("\n⏹️  Evaluación interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error durante la evaluación: {e}")
        logger.error(f"Error en evaluación: {e}")

def safe_json_serializer(obj):
    """
    Serializador JSON seguro que convierte valores problemáticos a null.
    
    Args:
        obj: Objeto a serializar
        
    Returns:
        Objeto serializable o None para valores problemáticos
    """
    if isinstance(obj, float):
        if math.isnan(obj):
            return None  # NaN -> null
        elif math.isinf(obj):
            return None  # Inf -> null
    return obj

def safe_json_dumps(data, **kwargs):
    """
    Función wrapper para json.dumps con manejo seguro de valores nulos.
    
    Args:
        data: Datos a serializar
        **kwargs: Argumentos adicionales para json.dumps
        
    Returns:
        String JSON con valores nulos seguros
    """
    return json.dumps(data, default=safe_json_serializer, **kwargs)

def clean_data_for_json(data):
    """
    Limpia datos recursivamente para serialización JSON segura.
    
    Args:
        data: Datos a limpiar (dict, list, o cualquier tipo)
        
    Returns:
        Datos limpios sin valores NaN o Inf
    """
    if isinstance(data, dict):
        return {k: clean_data_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    elif isinstance(data, float):
        if math.isnan(data) or math.isinf(data):
            return None
    return data

if __name__ == "__main__":
    main()
