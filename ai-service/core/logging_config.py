import logging
import logging.handlers
from pathlib import Path


def setup_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    fmt = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 (INFO 이상)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    # 파일 (DEBUG 이상, 자정 롤링, 30일 보관)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "ai-service.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmt)
    file_handler.suffix = "%Y-%m-%d"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(console)
    root.addHandler(file_handler)

    # 서드파티 노이즈 억제
    for noisy in ("httpx", "httpcore", "LiteLLM", "openai", "litellm"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("crewai").setLevel(logging.INFO)
