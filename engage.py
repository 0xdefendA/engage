import argparse
from engage.main import main


def parse_args():
    parser = argparse.ArgumentParser(
        description="Engage - AI-powered SOC operations assistant"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "test", "production"],
        default="development",
        help="Choose the configuration environment",
    )
    parser.add_argument(
        "--playbook",
        help="Which playbook to use",
        required=True,
    )


    arguments = parser.parse_args()
    return arguments

if __name__ == "__main__":
    args= parse_args()
    main(args)