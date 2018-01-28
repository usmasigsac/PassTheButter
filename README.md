# launcher
Live CTF tool for launching and managing exploits.

## Capabilities:
    - auto-loading / attack of python exploits
        - can use third party libraries
        - multi-threaded
        - group/indiv. scheduling
        - able to send fake traffic
    - configuration from json file
    - automatic score submission
        - configurable with options:
            1) post to http
            2) post to socket
            3) auth with token
            4) auth with user/pass
    - crash-safe
    - interactive cli
        - tab completion and help
    - example exploits
        - web
        - socket
        - pwntools
    -logging