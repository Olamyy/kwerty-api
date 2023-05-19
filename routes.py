from fastapi import APIRouter
from pydantic import BaseModel
from services.metrics_manager import MetricsManager
from services.prompt_manager import KorPromptManager

router = APIRouter()


class UserText(BaseModel):
    text: str


@router.post("/evaluate/")
async def evaluate_text(user_text: UserText):
    user_text = user_text.text
    prompt_manager = KorPromptManager(user_text=user_text)
    prompt_result = prompt_manager.run()
    data = prompt_result["data"]
    metrics = MetricsManager(data["country"])
    processed_metrics = metrics.process_metrics()
    return processed_metrics
