#!/usr/bin/env python3
"""
Automated Notebook Execution with Configuration

Runs Jupyter notebooks with configurable timeouts, skip lists, and caching.
Supports both Python and R notebooks with automatic kernel detection.
Configuration is read from notebook_config.json.

Original Repository: https://github.com/dhopp1/nowcasting_benchmark
Reproduction/Extension: Sermet Pekin (https://github.com/SermetPekin/nowcasting_benchmark)
Purpose: Extend and reproduce functionality with modern package compatibility
Date: November 2025
License: MIT

NOTE: This is ongoing work to verify reproduction in a specific environment.
      Not all code has been fully tested and verified yet.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
import sys
import argparse
import glob
import re

# Configuration file
CONFIG_FILE = Path("notebook_config.json")

def load_config():
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        print(f"❌ Error: Configuration file {CONFIG_FILE} not found!")
        print("Please create notebook_config.json with execution settings.")
        sys.exit(1)
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            print(f"✓ Loaded configuration from {CONFIG_FILE}")
            return config
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)

def get_notebooks_from_patterns(config):
    """Get list of notebooks matching include/exclude patterns."""
    patterns = config.get("notebook_patterns", {})
    include_patterns = patterns.get("include", ["methodologies/*.ipynb"])
    exclude_patterns = patterns.get("exclude", [])
    
    notebooks = set()
    
    # Add notebooks matching include patterns
    for pattern in include_patterns:
        matched_files = glob.glob(pattern)
        notebooks.update(Path(f).name for f in matched_files)
    
    # Remove notebooks matching exclude patterns
    for pattern in exclude_patterns:
        matched_files = glob.glob(pattern)
        for f in matched_files:
            notebooks.discard(Path(f).name)
    
    return sorted(notebooks)

def get_timeout_for_notebook(notebook_name, config):
    """Get timeout for a specific notebook based on its category."""
    categories = config.get("categories", {})
    category = categories.get(notebook_name, None)
    
    timeout_config = config["execution"]["timeout_by_category"]
    default_timeout = config["execution"]["default_timeout"]
    multiplier = config["execution"]["global_timeout_multiplier"]
    
    if category and category in timeout_config:
        base_timeout = timeout_config[category]
    else:
        base_timeout = default_timeout
    
    return int(base_timeout * multiplier)

def should_skip_notebook(notebook_name, config):
    """Check if notebook should be skipped."""
    skip_list = config.get("skip_notebooks", {})
    return notebook_name in skip_list

def get_skip_reason(notebook_name, config):
    """Get reason why notebook is skipped."""
    skip_list = config.get("skip_notebooks", {})
    return skip_list.get(notebook_name, "Unknown reason")

def load_cache(cache_file):
    """Load execution cache from file."""
    if not cache_file.exists():
        return {}
    
    try:
        with open(cache_file, 'r') as f:
            cache = json.load(f)
            print(f"✓ Loaded cache from {cache_file} ({len(cache)} entries)")
            return cache
    except Exception as e:
        print(f"⚠️  Warning: Could not load cache: {e}")
        return {}

def save_cache(cache, cache_file):
    """Save execution cache to file."""
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
        print(f"✓ Cache saved to {cache_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not save cache: {e}")

def execute_notebook(notebook_path, timeout):
    """Execute a notebook and return (success, duration, error_msg)."""
    print(f"  ⏳ Executing {notebook_path.name}...")
    
    # Determine kernel based on notebook type
    is_r_notebook = notebook_path.name.startswith('r_')
    
    # Check for virtual environment
    venv_python = Path(".venv/bin/python3")
    if venv_python.exists():
        jupyter_cmd = str(venv_python.parent / "jupyter")
        python_path = str(venv_python.resolve())
        
        # Set environment to use venv Python
        env = os.environ.copy()
        env['VIRTUAL_ENV'] = str(venv_python.parent.parent.resolve())
        env['PATH'] = f"{venv_python.parent}:{env.get('PATH', '')}"
        
        # Use appropriate kernel
        if is_r_notebook:
            kernel_name = "ir"
            print(f"  📊 Using R kernel: {kernel_name}")
        else:
            kernel_name = "nowcasting_venv"
            print(f"  📦 Using Python venv: {python_path}")
    else:
        jupyter_cmd = "jupyter"
        python_path = None
        env = None
        if is_r_notebook:
            kernel_name = "ir"
            print(f"  📊 Using R kernel: {kernel_name}")
        else:
            kernel_name = "python3"
            print(f"  ⚠️  No venv found, using system jupyter")
    
    start_time = time.time()
    try:
        cmd = [
            jupyter_cmd, "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            f"--ExecutePreprocessor.kernel_name={kernel_name}",
            "--ExecutePreprocessor.timeout={}".format(timeout),
            str(notebook_path)
        ]
        
        # Run with venv environment
        result = subprocess.run(
            cmd,
            timeout=timeout + 10,  # Give extra time for process overhead
            env=env,
            stdout=None,  # Stream output to terminal
            stderr=None   # Stream errors to terminal
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            return True, duration, None
        else:
            return False, duration, f"nbconvert failed with exit code {result.returncode}"
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return False, duration, f"Timeout after {timeout}s"
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)

def format_duration(seconds):
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def save_results(results, results_file):
    """Save execution results to CSV."""
    try:
        with open(results_file, 'w', newline='') as f:
            f.write('notebook,status,duration_sec,duration_formatted,category,timestamp,error\n')
            
            for result in results:
                error = result.get('error', '').replace('"', '""')
                duration_val = result["duration"] if result["duration"] is not None else 0
                f.write(f'{result["notebook"]},{result["status"]},'
                       f'{duration_val:.2f},'
                       f'{result["duration_formatted"]},{result["category"]},'
                       f'{result["timestamp"]},"{error}"\n')
        
        print(f"\n✓ Results saved to {results_file}")
    except Exception as e:
        print(f"⚠️  Warning: Could not save results: {e}")

def print_summary(results):
    """Print execution summary."""
    print("\n" + "="*70)
    print("EXECUTION SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r['status'] == 'success']
    failed = [r for r in results if r['status'] == 'failed']
    cached = [r for r in results if r['status'] == 'cached']
    skipped = [r for r in results if r['status'] == 'skipped']
    
    print(f"\n✓ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"💾 Cached: {len(cached)}")
    print(f"⏭️  Skipped: {len(skipped)}")
    print(f"📊 Total: {len(results)}")
    
    if successful:
        total_time = sum(r['duration'] for r in successful)
        print(f"\n⏱️  Total execution time: {format_duration(total_time)}")
        print(f"   Average time: {format_duration(total_time / len(successful))}")
    
    if failed:
        print("\n❌ Failed notebooks:")
        for r in failed:
            print(f"   - {r['notebook']}: {r.get('error', 'Unknown error')[:100]}")

def main():
    parser = argparse.ArgumentParser(
        description='Execute Jupyter notebooks with caching and configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Configuration is read from notebook_config.json. 

Options:
  --force           Clear cache and re-run all notebooks
  --config FILE     Use alternate configuration file (default: notebook_config.json)
  --multiplier N    Multiply all timeouts by N (e.g., 2.0 for double timeout)
  --dry-run         Show what would be executed without running
  
Examples:
  %(prog)s                    # Run with cached results
  %(prog)s --force            # Clear cache and re-run all
  %(prog)s --multiplier 2.0   # Run with 2x timeout
  %(prog)s --dry-run          # Preview execution plan
        """
    )
    
    parser.add_argument('--force', action='store_true',
                       help='Clear cache and re-run all notebooks')
    parser.add_argument('--config', type=str, default='notebook_config.json',
                       help='Configuration file path')
    parser.add_argument('--multiplier', type=float,
                       help='Timeout multiplier (overrides config)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show execution plan without running')
    
    args = parser.parse_args()
    
    # Update config file path if specified
    global CONFIG_FILE
    CONFIG_FILE = Path(args.config)
    
    # Load configuration
    config = load_config()
    
    # Override timeout multiplier if specified
    if args.multiplier:
        config["execution"]["global_timeout_multiplier"] = args.multiplier
        print(f"✓ Using timeout multiplier: {args.multiplier}x")
    
    # Setup paths
    methodologies_dir = Path("methodologies")
    cache_file = Path(config["cache"]["cache_file"])
    results_file = Path(config["output"]["results_file"])
    
    # Load cache (unless force flag is set)
    if args.force or not config["cache"]["enabled"]:
        print("🔄 Force mode: Clearing cache and re-running all notebooks")
        cache = {}
        if cache_file.exists():
            cache_file.unlink()
    else:
        cache = load_cache(cache_file) if config["cache"]["enabled"] else {}
    
    # Get notebooks to process
    notebooks = get_notebooks_from_patterns(config)
    print(f"\n📓 Found {len(notebooks)} notebooks matching patterns")
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - Execution Plan:")
        print("-" * 70)
    
    results = []
    
    for notebook_name in notebooks:
        notebook_path = methodologies_dir / notebook_name
        
        # Get configuration for this notebook
        category = config.get("categories", {}).get(notebook_name, "unknown")
        timeout = get_timeout_for_notebook(notebook_name, config)
        
        # Check if should skip
        if should_skip_notebook(notebook_name, config):
            reason = get_skip_reason(notebook_name, config)
            print(f"\n⏭️  Skipping {notebook_name}: {reason}")
            results.append({
                'notebook': notebook_name,
                'status': 'skipped',
                'duration': None,
                'duration_formatted': 'N/A',
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'error': reason
            })
            continue
        
        # Check cache
        if notebook_name in cache and not args.force:
            cached_result = cache[notebook_name]
            print(f"\n💾 Using cached result for {notebook_name} "
                  f"({cached_result['duration_formatted']}, {category})")
            results.append({
                'notebook': notebook_name,
                'status': 'cached',
                'duration': cached_result['duration'],
                'duration_formatted': cached_result['duration_formatted'],
                'category': category,
                'timestamp': cached_result['timestamp'],
                'error': ''
            })
            continue
        
        # Show execution plan in dry-run mode
        if args.dry_run:
            print(f"Would execute: {notebook_name} (timeout: {timeout}s, category: {category})")
            continue
        
        # Execute notebook
        print(f"\n▶️  Running {notebook_name} (timeout: {timeout}s, category: {category})")
        
        if not notebook_path.exists():
            print(f"  ❌ File not found: {notebook_path}")
            results.append({
                'notebook': notebook_name,
                'status': 'failed',
                'duration': 0,
                'duration_formatted': '0s',
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'error': 'File not found'
            })
            continue
        
        success, duration, error = execute_notebook(notebook_path, timeout)
        duration_formatted = format_duration(duration)
        
        if success:
            print(f"  ✓ Success! Duration: {duration_formatted}")
            result = {
                'notebook': notebook_name,
                'status': 'success',
                'duration': duration,
                'duration_formatted': duration_formatted,
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'error': ''
            }
            # Cache successful result
            cache[notebook_name] = result
            save_cache(cache, cache_file)
        else:
            print(f"  ❌ Failed! Duration: {duration_formatted}")
            print(f"  Error: {error}")
            result = {
                'notebook': notebook_name,
                'status': 'failed',
                'duration': duration,
                'duration_formatted': duration_formatted,
                'category': category,
                'timestamp': datetime.now().isoformat(),
                'error': error or 'Unknown error'
            }
        
        results.append(result)
    
    if args.dry_run:
        print("\n✓ Dry run complete. Use without --dry-run to execute.")
        return
    
    # Save results
    save_results(results, results_file)
    
    # Print summary
    print_summary(results)
    
    print("\n" + "="*70)
    print(f"📄 Detailed results: {results_file}")
    print(f"💾 Cache file: {cache_file}")
    print(f"⚙️  Configuration: {CONFIG_FILE}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
