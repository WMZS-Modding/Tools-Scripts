import json
import sys
import os
from typing import Dict, List, Any, Optional
import time
import argparse
import gc

class ChartMerger:
    def __init__(self):
        self.total_notes = 0
        self.total_events = 0
        self.start_time = time.time()

    def print_progress(self, message: str):
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:.2f}s] {message}")

    def load_chart(self, path: str) -> Optional[Dict[str, Any]]:
        self.print_progress(f"Loading: {path}")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'song' in data and isinstance(data['song'], dict):
                chart = data['song']
                has_wrapper = True
            else:
                chart = data
                has_wrapper = False

            note_count = 0
            if 'notes' in chart:
                for section in chart['notes']:
                    if 'sectionNotes' in section:
                        note_count += len(section['sectionNotes'])

            event_count = len(chart.get('events', []))

            self.total_notes += note_count
            self.total_events += event_count

            self.print_progress(f"  Loaded: {note_count} notes, {event_count} events")

            return {'chart': chart, 'has_wrapper': has_wrapper}
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None


    def detect_indentation(self, path: str) -> Optional[int]:
        """Detect indentation style from file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                first_lines = [f.readline() for _ in range(10)]

            for line in first_lines:
                if line.startswith('\t'):
                    return None
                if line.startswith('    '):
                    return 4
                if line.startswith('  '):
                    return 2
            return None
        except:
            return None

    def merge_charts(self, chart_paths: List[str], output_path: str, use_indentation: Optional[bool] = None) -> bool:
        if len(chart_paths) < 2:
            print("Error: Need at least 2 charts to merge")
            return False

        self.print_progress(f"Starting merge of {len(chart_paths)} charts")

        if use_indentation is None:
            detected_indent = self.detect_indentation(chart_paths[0])
            if detected_indent is not None:
                use_indentation = True
                self.print_progress(f"Detected indentation: {detected_indent} spaces")
            else:
                use_indentation = False
                self.print_progress("No indentation detected, using compact output")

        base_data = self.load_chart(chart_paths[0])
        if not base_data:
            return False

        base_chart = base_data['chart']
        has_wrapper = base_data['has_wrapper']

        if 'notes' not in base_chart:
            base_chart['notes'] = []
        if 'events' not in base_chart:
            base_chart['events'] = []

        for i in range(1, len(chart_paths)):
            self.print_progress(f"Merging chart {i+1}/{len(chart_paths)}")

            next_data = self.load_chart(chart_paths[i])
            if not next_data:
                continue

            next_chart = next_data['chart']

            if 'notes' in next_chart:
                next_notes = next_chart['notes']
                base_notes = base_chart['notes']

                for section_idx in range(len(next_notes)):
                    next_section = next_notes[section_idx]

                    if section_idx < len(base_notes):
                        base_section = base_notes[section_idx]
                        if 'sectionNotes' in next_section:
                            if 'sectionNotes' not in base_section:
                                base_section['sectionNotes'] = []
                            base_section['sectionNotes'].extend(next_section['sectionNotes'])
                    else:
                        base_notes.append(next_section)

            if 'events' in next_chart:
                base_chart['events'].extend(next_chart['events'])

            next_chart = None
            next_data = None

            self.print_progress(f"  Progress: {self.total_notes} notes, {self.total_events} events")

        self.print_progress("Saving merged chart...")
        self.save_chart(base_chart, output_path, has_wrapper, use_indentation)

        self.print_progress(f"Complete! Total: {self.total_notes} notes, {self.total_events} events")
        return True

    def save_chart(self, chart: Dict[str, Any], path: str, has_wrapper: bool, use_indentation: bool):
        if has_wrapper:
            output = {'song': chart}
        else:
            output = chart

        indent = 4 if use_indentation else None

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=indent, ensure_ascii=False)

        self.print_progress(f"Saved to: {path}")

def main():
    parser = argparse.ArgumentParser(description='Merge multiple chart files')
    parser.add_argument('-i', '--input', nargs='+', help='Input file paths')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--indent', action='store_true', help='Force indentation in output')
    parser.add_argument('--no-indent', action='store_true', help='Force compact output (no indentation)')
    args = parser.parse_args()

    output_path = args.output
    input_paths = args.input

    for path in input_paths:
        if not os.path.exists(path):
            print(f"Error: File not found: {path}")
            sys.exit(1)

    use_indentation = None
    if args.indent:
        use_indentation = True
    elif args.no_indent:
        use_indentation = False

    merger = ChartMerger()
    success = merger.merge_charts(input_paths, output_path, use_indentation=use_indentation)

    if success:
        print("\nMerge completed successfully!")
        sys.exit(0)
    else:
        print("\nMerge failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()