"""
Batch request processor for CSV/TXT input files.
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from src.client import APIClient
from src.config import Config
from src.output import save_output


class BatchProcessor:
    """Process batch requests from CSV or TXT files."""

    def __init__(
        self,
        config: Config,
        output_format: str = 'json',
        output_path: str = './output',
        include_timestamp: bool = False,
        timestamp_format: str = '%Y%m%d_%H%M%S',
    ):
        self.config = config
        self.client = APIClient(config)
        self.output_format = output_format
        self.output_path = Path(output_path)
        self.include_timestamp = include_timestamp
        self.timestamp_format = timestamp_format
        self.output_path.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Process input file (CSV or TXT)."""
        file_path = Path(file_path)

        if file_path.suffix.lower() == '.csv':
            requests_list = self._parse_csv(file_path)
        elif file_path.suffix.lower() == '.txt':
            requests_list = self._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        results = []
        for request_data in requests_list:
            try:
                result = self._execute_request(request_data)
                results.append(result)
                print(f"✅ Processed: {request_data.get('endpoint', 'unknown')}")
            except Exception as e:
                print(f"❌ Failed: {e}")
                results.append({"error": str(e)})

        self._save_results(results)
        return results

    def _parse_csv(self, file_path: Path) -> List[Dict]:
        """Parse CSV file."""
        requests_list = []
        with open(file_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                requests_list.append(dict(row))
        return requests_list

    def _parse_txt(self, file_path: Path) -> List[Dict]:
        """Parse TXT file (JSON lines format)."""
        requests_list = []
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    requests_list.append(json.loads(line))
        return requests_list

    def _execute_request(self, request_data: Dict) -> Dict:
        """Execute a single request."""
        method = request_data.get('method', 'GET').upper()
        endpoint = request_data.get('endpoint', '/')

        if method == 'GET':
            return self.client.get(endpoint)
        elif method == 'POST':
            return self.client.post(endpoint, request_data.get('data', {}))
        elif method == 'PUT':
            return self.client.put(endpoint, request_data.get('data', {}))
        elif method == 'DELETE':
            return self.client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def _save_results(self, results: List[Dict]):
        """Save results in specified format."""
        output_file = save_output(
            payload=results,
            output_format=self.output_format,
            output_dir=str(self.output_path),
            stem="results",
            include_timestamp=self.include_timestamp,
            timestamp_format=self.timestamp_format,
        )
        print(f"Results saved to: {output_file}")
