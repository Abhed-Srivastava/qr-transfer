import os
import glob
from encoder import FileEncoder
import config

class RecoverySystem:
    def __init__(self, decoder):
        self.decoder = decoder

    def identify_missing(self):
        return self.decoder.get_missing_chunks()

    def generate_recovery_report(self):
        missing = self.identify_missing()
        if not missing:
            return "No chunks missing. File ready for reassembly."
        
        report = f"Missing {len(missing)} chunks out of {self.decoder.total_chunks}:\n"
        report += ", ".join(map(str, missing[:20]))
        if len(missing) > 20:
            report += " ..."
        return report

    def save_recovery_request(self, path="recovery_request.txt"):
        missing = self.identify_missing()
        with open(path, 'w') as f:
            f.write(f"Session: {self.decoder.session_id}\n")
            f.write(f"Missing Chunks: {','.join(map(str, missing))}\n")
        return path
