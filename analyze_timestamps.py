import re
from datetime import datetime

def parse_log_file(log_file_path, threshold_seconds=30):
    """
    Analyzes log file and identifies lines where execution time exceeds threshold.
    
    Args:
        log_file_path: Path to the log file
        threshold_seconds: Minimum time gap to report (default: 30 seconds)
    
    Returns:
        List of tuples containing (line_num, time_gap, prev_timestamp, curr_timestamp, line_content)
    """
    time_consuming_steps = []
    
    with open(log_file_path, 'r') as f:
        lines = f.readlines()
    
    prev_timestamp = None
    prev_line_num = None
    
    # Regex pattern to match timestamps: YYYY-MM-DD HH:MM:SS,mmm
    timestamp_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})'
    
    for line_num, line in enumerate(lines, start=1):
        match = re.match(timestamp_pattern, line.strip())
        
        if match:
            timestamp_str = match.group(1)
            # Parse timestamp
            curr_timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            
            if prev_timestamp:
                # Calculate time difference
                time_diff = (curr_timestamp - prev_timestamp).total_seconds()
                
                if time_diff >= threshold_seconds:
                    time_consuming_steps.append({
                        'prev_line': prev_line_num,
                        'curr_line': line_num,
                        'time_gap': time_diff,
                        'prev_timestamp': prev_timestamp,
                        'curr_timestamp': curr_timestamp,
                        'prev_content': lines[prev_line_num - 1].strip(),
                        'curr_content': line.strip()
                    })
            
            prev_timestamp = curr_timestamp
            prev_line_num = line_num
    
    return time_consuming_steps


def print_analysis(time_consuming_steps, top_n=20):
    """
    Prints analysis of time-consuming steps.
    
    Args:
        time_consuming_steps: List of time-consuming operations
        top_n: Number of top results to display
    """
    if not time_consuming_steps:
        print("No time-consuming steps found.")
        return
    
    # Sort by time gap (descending)
    sorted_steps = sorted(time_consuming_steps, key=lambda x: x['time_gap'], reverse=True)
    
    print(f"\n{'='*100}")
    print(f"TIME-CONSUMING OPERATIONS (threshold >= 30 seconds)")
    print(f"{'='*100}\n")
    print(f"Total operations found: {len(sorted_steps)}\n")
    
    print(f"Top {min(top_n, len(sorted_steps))} slowest operations:\n")
    print(f"{'Rank':<6} {'Lines':<15} {'Time (sec)':<12} {'Time (min)':<12} {'Timestamps':<40}")
    print(f"{'-'*100}")
    
    for idx, step in enumerate(sorted_steps[:top_n], start=1):
        lines_range = f"{step['prev_line']}-{step['curr_line']}"
        time_sec = f"{step['time_gap']:.2f}s"
        time_min = f"{step['time_gap']/60:.2f}min"
        timestamps = f"{step['prev_timestamp'].strftime('%H:%M:%S')} → {step['curr_timestamp'].strftime('%H:%M:%S')}"
        
        print(f"{idx:<6} {lines_range:<15} {time_sec:<12} {time_min:<12} {timestamps:<40}")
    
    # Statistics
    print(f"\n{'-'*100}")
    print("\nSTATISTICS:")
    print(f"  Average time gap: {sum(s['time_gap'] for s in sorted_steps) / len(sorted_steps):.2f} seconds")
    print(f"  Maximum time gap: {sorted_steps[0]['time_gap']:.2f} seconds (lines {sorted_steps[0]['prev_line']}-{sorted_steps[0]['curr_line']})")
    print(f"  Minimum time gap: {sorted_steps[-1]['time_gap']:.2f} seconds")
    
    # Pattern analysis
    print(f"\n{'-'*100}")
    print("\nPATTERN ANALYSIS:")
    
    # Count operations related to specific patterns
    decrease_ops = sum(1 for s in sorted_steps if 'DECREASE' in s['curr_content'])
    increase_ops = sum(1 for s in sorted_steps if 'INCREASE' in s['curr_content'])
    k_neg_adj_ops = sum(1 for s in sorted_steps if 'K_neg_adj' in s['curr_content'])
    
    print(f"  Operations with DECREASE effect: {decrease_ops}")
    print(f"  Operations with INCREASE effect: {increase_ops}")
    print(f"  Operations with K_neg_adj: {k_neg_adj_ops}")
    
    print(f"\n{'='*100}\n")


def save_to_file(time_consuming_steps, output_file):
    """
    Saves analysis to a text file.
    
    Args:
        time_consuming_steps: List of time-consuming operations
        output_file: Output file path
    """
    sorted_steps = sorted(time_consuming_steps, key=lambda x: x['time_gap'], reverse=True)
    
    with open(output_file, 'w') as f:
        f.write("TIME-CONSUMING OPERATIONS REPORT\n")
        f.write("=" * 100 + "\n\n")
        
        for idx, step in enumerate(sorted_steps, start=1):
            f.write(f"Operation #{idx}\n")
            f.write(f"  Lines: {step['prev_line']} → {step['curr_line']}\n")
            f.write(f"  Time gap: {step['time_gap']:.2f} seconds ({step['time_gap']/60:.2f} minutes)\n")
            f.write(f"  Previous line: {step['prev_content']}\n")
            f.write(f"  Current line: {step['curr_content']}\n")
            f.write(f"  Timestamps: {step['prev_timestamp']} → {step['curr_timestamp']}\n")
            f.write("-" * 100 + "\n\n")
    
    print(f"Detailed report saved to: {output_file}")


if __name__ == "__main__":
    import sys
    
    # Configuration
    log_file = "execute_policy_analyse2.log"
    threshold = 30  # seconds
    output_report = "timing_analysis_report.txt"
    
    # Allow command-line arguments
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    if len(sys.argv) > 2:
        threshold = int(sys.argv[2])
    
    print(f"Analyzing log file: {log_file}")
    print(f"Threshold: {threshold} seconds\n")
    
    # Analyze the log file
    results = parse_log_file(log_file, threshold)
    
    # Print analysis to console
    print_analysis(results, top_n=20)
    
    # Save detailed report to file
    save_to_file(results, output_report)