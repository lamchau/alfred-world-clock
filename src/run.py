import sys

# thin entry stub: the entry script is never cached to .pyc by cpython, so keep
# it trivial and delegate to main, which imports as a cached module. this avoids
# recompiling the bulk of the workflow on every invocation.
import main

if __name__ == "__main__":
    main.run()
    sys.exit()
