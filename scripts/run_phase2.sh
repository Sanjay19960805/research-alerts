#!/usr/bin/env python3
from typing import Dict


def calculate_cost(input_tokens: int, output_tokens: int, input_rate_per_1k: float, output_rate_per_1k: float) -> float:
    input_cost = (input_tokens / 1000.0) * input_rate_per_1k
    output_cost = (output_tokens / 1000.0) * output_rate_per_1k
    return input_cost + output_cost


def summarize_cost(token_cfg: Dict[str, float], input_tokens: int, output_tokens: int) -> Dict[str, float]:
    input_rate = float(token_cfg.get("input_rate_per_1k", 0.0))
    output_rate = float(token_cfg.get("output_rate_per_1k", 0.0))
    total_cost = calculate_cost(input_tokens, output_tokens, input_rate, output_rate)
    return {
        "input_tokens": float(input_tokens),
        "output_tokens": float(output_tokens),
        "total_cost": float(total_cost),
        "input_rate_per_1k": float(input_rate),
        "output_rate_per_1k": float(output_rate),
    }
