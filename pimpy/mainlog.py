import logging, sys  # noqa:F401

try: import structlog
except ImportError: structlog = None
try: import colorama
except ImportError: colorama = None

log = logging.getLogger(__name__)

stdlib_stream_handler = None

def setup_structlog(level=logging.INFO, allow_reattach=False):
    """setup_structlog sets up colored structlog logging and
    adds a structlog formatter to stdlib logging.
    """

    if structlog is None:
        logging.basicConfig(level=level)
        log.error(SystemError("please install structlog"))
        return

    use_colors = colorama is not None

    log_procs = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(processors     = log_procs,
                        logger_factory = structlog.stdlib.LoggerFactory(),
                        cache_logger_on_first_use = True)

    root = logging.getLogger()

    global stdlib_stream_handler
    if stdlib_stream_handler is not None:
        if allow_reattach:
            root.removeHandler(stdlib_stream_handler)
            log.debug('Reattaching structlog formatter to stdlib root logger.')
        else:
            log.warn('Skipping to reattach structlog formatter to stdlib root logger. '
                     'Please use allow_reattach = True.')
            return

    formatter = structlog.stdlib.ProcessorFormatter(
        processor         = structlog.dev.ConsoleRenderer(colors=use_colors),
        foreign_pre_chain = [
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
        ]
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(level)
    stdlib_stream_handler = handler

    _log = structlog.get_logger(__name__)
    _log.debug("setup structlog level={}".format(logging.getLevelName(level)), use_colors=use_colors)


def setup_logging(level=logging.INFO, use_structlog=False, allow_reattach=False):
    """setup_logging sets up stdlib or structlog logging with to the given level.
    If use_structlog is True, it also sets up structlog logging with convenient defaults
    for human-readable logs.
    """
    if use_structlog:
        setup_structlog(level=level, allow_reattach=allow_reattach)
    else:
        logging.basicConfig(level=level)
        logging.getLogger().setLevel(level)

    log.debug('setup logging, level=%s', logging.getLevelName(level))
