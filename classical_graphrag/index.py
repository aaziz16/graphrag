import argparse
import os
import sys
from graphrag.index.cli import index_cli

def main():
    # Set the default root to the current directory and config to settings.yaml
    default_root = os.getcwd()  # Get the current working directory
    default_config = "settings.yaml"  # Default config file

    # Filter out unwanted arguments
    filtered_args = [arg for arg in sys.argv if not arg.startswith('--f=')]
    
    parser = argparse.ArgumentParser(description="Run GraphRAG indexing with various options.")
    parser.add_argument(
        "--config",
        help="The configuration YAML file to use when running the pipeline.",
        required=False,
        type=str,
        default=default_config,  # Set default config file
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Runs the pipeline with verbose logging.",
        action="store_true",
    )
    parser.add_argument(
        "--memprofile",
        help="Runs the pipeline with memory profiling.",
        action="store_true",
    )
    parser.add_argument(
        "--root",
        help="Root directory for input and output data if no configuration is defined.",
        required=False,
        type=str,
        default=default_root,  # Set default root directory
    )
    parser.add_argument(
        "--resume",
        help="Resume a given data run leveraging Parquet output files.",
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "--reporter",
        help="The progress reporter to use. Valid values are 'rich', 'print', or 'none'.",
        type=str,
        choices='print',
    )
    parser.add_argument(
        "--emit",
        help="Data formats to emit, comma-separated. Valid values are 'parquet' and 'csv'. Default='parquet,csv'.",
        type=str,
        default="parquet",  # Setting a default value
    )
    parser.add_argument(
        "--dryrun",
        help="Run the pipeline without actually executing any steps and inspect the configuration.",
        action="store_true",
    )
    parser.add_argument("--nocache", help="Disable LLM cache.", action="store_true")
    parser.add_argument(
        "--init",
        help="Create an initial configuration in the given path.",
        action="store_true",
    )

    # Parse the filtered arguments
    args = parser.parse_args(filtered_args[1:])  # Skip the script name at index 0

    # Call index_cli with parsed arguments
    index_cli(
        root=args.root,
        overlay_defaults=True,
        verbose=args.verbose,
        resume=args.resume,
        memprofile=args.memprofile,
        nocache=args.nocache,
        reporter=args.reporter,
        config=args.config,
        emit=args.emit,
        dryrun=args.dryrun,
        init=args.init,
        cli=True,
    )

if __name__ == "__main__":
    main()
