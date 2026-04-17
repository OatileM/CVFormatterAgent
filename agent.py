"""Agent configuration for the CV Formatter Agent.

Creates and returns a configured Strands ``Agent`` instance that orchestrates
the five CV formatting tools in the correct order.
"""

from __future__ import annotations

import os

from strands import Agent

from tools.analyze_keywords import analyze_keywords
from tools.extract_keywords import extract_keywords
from tools.generate_output import generate_output
from tools.parse_cv import parse_cv
from tools.reformat_cv import reformat_cv

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert ATS (Applicant Tracking System) optimisation specialist.
Your job is to reformat a user's CV so that it achieves the highest possible
ATS score for a given job specification.

Follow these steps in order:

STEP 1 — parse_cv
Call parse_cv with the CV file path.

STEP 2 — extract_keywords
Read the job specification carefully. YOU must identify all skills, tools,
technologies, certifications, and job titles. Classify each as:
  - "required": "must have", "required", "essential", "mandatory", or no qualifier
  - "preferred": "nice to have", "preferred", "bonus", "desirable"
Produce a JSON array, then call extract_keywords with it:
  [{"term": "Python", "classification": "required"}, ...]

STEP 3 — analyze_keywords
Call analyze_keywords with no arguments. It reads from session state.

STEP 4 — reformat_cv
YOU must rewrite the CV following ALL these rules:
  - Use ONLY: Summary, Work Experience, Education, Skills, Certifications, Projects
  - Single-column plain text — no tables, pipes, graphics, non-ASCII characters
  - All dates in MM/YYYY format only
  - Skills section MUST appear immediately after Summary
  - Incorporate absent required keywords where experience genuinely supports it
  - Preserve ALL facts — no fabrication whatsoever
Then call reformat_cv passing the full reformatted text.

STEP 5 — generate_output
Call generate_output with the output_dir argument.

ERROR HANDLING:
If any tool returns a JSON string containing "tool_name", it is a ToolError.
Stop immediately and report the error to the user.
"""

# ---------------------------------------------------------------------------
# Default model configuration
# ---------------------------------------------------------------------------
_DEFAULT_MODEL_ID = "YOUR ARN AND INFERENCE PROFILE"
# EXAMPLE arn:aws:bedrock:us-east-1:79963456456456396330:application-inference-profile/kfd2p343FHFDFGfu4e2v



# ---------------------------------------------------------------------------
# Public factory function
# ---------------------------------------------------------------------------


def create_agent() -> Agent:
    """Create and return a configured Strands Agent instance.

    Reads ``MODEL_PROVIDER`` and ``MODEL_ID`` from environment variables.
    Defaults to Amazon Bedrock with Claude Haiku 4.5 when the environment
    variables are absent.

    Returns:
        A fully configured ``Agent`` instance with all five CV formatting tools
        registered and the ATS optimisation system prompt applied.
    """
    model_provider = os.environ.get("MODEL_PROVIDER", "bedrock").lower()
    model_id = os.environ.get("MODEL_ID", _DEFAULT_MODEL_ID)

    tools = [
        parse_cv,
        extract_keywords,
        analyze_keywords,
        reformat_cv,
        generate_output,
    ]

    if model_provider == "bedrock":
        from strands.models import BedrockModel

        model = BedrockModel(model_id=model_id)
        return Agent(
            model=model,
            system_prompt=_SYSTEM_PROMPT,
            tools=tools,
        )

    # Fallback: let Strands use its default model resolution with the given
    # model_id (e.g. for other providers that Strands supports natively).
    return Agent(
        system_prompt=_SYSTEM_PROMPT,
        tools=tools,
    )
