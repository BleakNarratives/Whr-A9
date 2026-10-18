import unittest
import os
import tempfile
import pickle

from src.core.scanners.security_scanner import SecurityScanner
from src.core.loom.models import LoomWeave, Lexeme, MetricType

class TestSecurityScanner(unittest.TestCase):

    def setUp(self):
        """Set up common resources for tests."""
        self.scanner = SecurityScanner()
        # Create a temporary directory for test files
        self.test_dir = os.path.join(os.getcwd(), "tests", "temp_security_test")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary files."""
        for file_path in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file_path))
        os.rmdir(self.test_dir)

    def create_test_file(self, filename, content):
        """Helper to create a temporary test file."""
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def get_security_issues(self, weave: LoomWeave):
        """Helper to extract security issues from a weave."""
        # Assuming the first metric is always the security one if it exists
        return [lexeme for lexeme in weave.lexemes.values() if lexeme.metrics and lexeme.metrics[0].metric_type == MetricType.SECURITY]

    def test_clean_file(self):
        """Test a file with no security issues."""
        content = """
def safe_function(x):
    y = x + 1
    return y

print('Hello, world!')
"""
        file_path = self.create_test_file('clean_file.py', content)
        weave = self.scanner.scan(file_path)
        issues = self.get_security_issues(weave)
        self.assertEqual(len(issues), 0)

    def test_eval_exec_detection(self):
        """Test detection of eval() and exec()."""
        content = """
def risky_eval():
    eval("danger")

def risky_exec():
    exec("danger")
"""
        file_path = self.create_test_file('risky_eval_exec.py', content)
        weave = self.scanner.scan(file_path)
        issues = self.get_security_issues(weave)
        self.assertEqual(len(issues), 2)
        self.assertTrue(any('eval()' in issue.label for issue in issues))
        self.assertTrue(any('exec()' in issue.label for issue in issues))

    def test_subprocess_shell_true(self):
        """Test detection of subprocess.run with shell=True."""
        content = """
import subprocess

def vulnerable_command():
    subprocess.run('ls -l', shell=True)

def safe_command():
    subprocess.run(['ls', '-l'])
"""
        file_path = self.create_test_file('subprocess_test.py', content)
        weave = self.scanner.scan(file_path)
        issues = self.get_security_issues(weave)
        self.assertEqual(len(issues), 1)
        self.assertTrue('subprocess.run with shell=True' in issues[0].label)

    def test_pickle_loads(self):
        """Test detection of pickle.loads."""
        content = """
import pickle

def unsafe_unpickle():
    data = None
    pickle.loads(data)
"""
        file_path = self.create_test_file('pickle_test.py', content)
        weave = self.scanner.scan(file_path)
        issues = self.get_security_issues(weave)
        self.assertEqual(len(issues), 1)
        self.assertTrue('pickle.loads' in issues[0].label)

    def test_syntax_error_handling(self):
        """Test graceful handling of syntax errors."""
        content = """
def broken_function():
    print('This will cause a syntax error'
"""
        file_path = self.create_test_file('syntax_error.py', content)
        # Expecting scan to complete without crashing, ideally with no issues found
        # (as it couldn't parse the code)
        try:
            weave = self.scanner.scan(file_path)
            issues = self.get_security_issues(weave)
            self.assertEqual(len(issues), 0) # No issues should be reported if parsing fails gracefully
        except Exception as e:
            self.fail(f"Scanning a file with syntax error raised an unexpected exception: {e}")

if __name__ == '__main__':
    unittest.main()
