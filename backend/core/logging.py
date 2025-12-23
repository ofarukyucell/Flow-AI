import logging 
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(level=logging.INFO) -> None:

        fmt = (
                '{"time":"%(asctime)s",'
                '"level":"%(levelname)s",'
                '"logger":"%(name)s",'
                '"msg":"%(message)s"}'
        )

        datefmt = "%Y-%m-%d %H:%M:%S"

        logging.basicConfig(level=level, format=fmt,datefmt=datefmt)

        log_dir=Path("logs")
        log_dir.mkdir(parents=True,exist_ok=True)
        
        file_handler=RotatingFileHandler(
                log_dir /"app.log",
                maxBytes=5_000_000,
                backupCount=5,
                encoding="utf-8")
        
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(fmt=fmt,datefmt=datefmt))
        logging.getLogger().addHandler(file_handler)

        for name in ("uvicorn","uvicorn.error","uvicorn.access"):
                lg=logging.getLogger(name)
                lg.handlers.clear()
                lg.propagate = True
