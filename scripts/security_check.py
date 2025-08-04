#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔐 ISKALA Security Validation Script
===================================

Comprehensive security check для валидации всех security fixes в Task 0.5.1.
Проверяет отсутствие hardcoded секретов, правильную конфигурацию и соответствие
security best practices.

Usage:
    python scripts/security_check.py --level=critical
    python scripts/security_check.py --level=all --fix
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import subprocess
from datetime import datetime

# Color codes для console output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
NC = '\033[0m'  # No Color

class SecurityIssue:
    """Represents a security issue found during scanning"""
    
    def __init__(self, severity: str, category: str, file_path: str, 
                 line_num: int, description: str, recommendation: str, 
                 evidence: str = ""):
        self.severity = severity
        self.category = category  
        self.file_path = file_path
        self.line_num = line_num
        self.description = description
        self.recommendation = recommendation
        self.evidence = evidence
    
    def __str__(self):
        color = RED if self.severity == "CRITICAL" else YELLOW if self.severity == "HIGH" else ""
        return (f"{color}[{self.severity}]{NC} {self.category}: {self.description}\n"
                f"  📁 File: {self.file_path}:{self.line_num}\n"
                f"  💡 Fix: {self.recommendation}\n"
                f"  🔍 Evidence: {self.evidence[:100]}...\n")

class ISKALASecurityScanner:
    """Comprehensive security scanner для ISKALA codebase"""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.issues: List[SecurityIssue] = []
        self.stats = {
            "files_scanned": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "hardcoded_secrets": 0
        }
        
        # Patterns для поиска hardcoded секретов
        self.secret_patterns = [
            # API Keys
            (r'sk-or-v1-[a-zA-Z0-9]{64}', "OpenRouter API Key", "CRITICAL"),
            (r'sk-[a-zA-Z0-9]{48,}', "Generic API Key", "CRITICAL"),
            (r'bearer\s+[a-zA-Z0-9]{32,}', "Bearer Token", "CRITICAL"),
            
            # Passwords
            (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password", "CRITICAL"),
            (r'PASSWORD\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password", "CRITICAL"),
            
            # Secret Keys
            (r'secret[_-]?key\s*=\s*["\'][^"\']{16,}["\']', "Secret Key", "CRITICAL"),
            (r'SECRET[_-]?KEY\s*=\s*["\'][^"\']{16,}["\']', "Secret Key", "CRITICAL"),
            
            # Database Credentials  
            (r'neo4j://[^:]+:[^@]+@', "Database URL with Credentials", "CRITICAL"),
            (r'redis://[^:]*:[^@]+@', "Redis URL with Credentials", "CRITICAL"),
            
            # Common weak secrets
            (r'iskala-secret-key-2024', "Default Secret Key", "CRITICAL"),
            (r'change_this_[a-zA-Z0-9_]+', "Placeholder Secret", "HIGH"),
        ]
        
        # File patterns для сканирования
        self.scan_extensions = {'.py', '.yml', '.yaml', '.json', '.env', '.sh', '.md'}
        self.exclude_patterns = {
            'node_modules', '__pycache__', '.git', 'venv', '.env.template', 
            'env.secure.template', 'test_', '.pytest_cache', 'SECURITY_ASSESSMENT_REPORT.md'
        }
    
    def should_scan_file(self, file_path: Path) -> bool:
        """Determine if file should be scanned"""
        if file_path.suffix not in self.scan_extensions:
            return False
            
        for exclude in self.exclude_patterns:
            if exclude in str(file_path):
                return False
                
        return True
    
    def scan_hardcoded_secrets(self, file_path: Path) -> List[SecurityIssue]:
        """Scan file for hardcoded secrets"""
        issues = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern, description, severity in self.secret_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Skip template files and comments explaining security
                        if any(skip in line.lower() for skip in ['template', 'example', 'placeholder', '# замените']):
                            continue
                            
                        issues.append(SecurityIssue(
                            severity=severity,
                            category="Hardcoded Secret",
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_num=line_num,
                            description=f"{description} found in code",
                            recommendation="Move to environment variable or secure vault",
                            evidence=match.group()[:50]
                        ))
                        self.stats["hardcoded_secrets"] += 1
                        
        except Exception as e:
            print(f"⚠️ Error scanning {file_path}: {e}")
            
        return issues
    
    def scan_api_security(self, file_path: Path) -> List[SecurityIssue]:
        """Scan for API security issues"""
        issues = []
        
        if not file_path.name.endswith('.py'):
            return issues
            
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for unprotected API endpoints
                if re.search(r'@app\.(post|get|put|delete)', line):
                    # Check if next lines have rate limiting or auth
                    context_lines = lines[max(0, line_num-3):line_num+3]
                    context = '\n'.join(context_lines)
                    
                    if '@limiter.limit' not in context and 'Depends(verify' not in context:
                        issues.append(SecurityIssue(
                            severity="HIGH",
                            category="Unprotected API Endpoint",
                            file_path=str(file_path.relative_to(self.root_path)),
                            line_num=line_num,
                            description="API endpoint without rate limiting or authentication",
                            recommendation="Add @limiter.limit() and Depends(verify_api_key)",
                            evidence=line.strip()
                        ))
                
                # Check for dangerous CORS settings
                if 'allow_origins=["*"]' in line:
                    issues.append(SecurityIssue(
                        severity="HIGH",
                        category="Insecure CORS",
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_num=line_num,
                        description="CORS allows all origins (*)",
                        recommendation="Specify exact allowed origins for production",
                        evidence=line.strip()
                    ))
                    
        except Exception as e:
            print(f"⚠️ Error scanning API security in {file_path}: {e}")
            
        return issues
    
    def scan_docker_security(self, file_path: Path) -> List[SecurityIssue]:
        """Scan Docker files for security issues"""
        issues = []
        
        if 'Dockerfile' not in file_path.name and not file_path.name.endswith('.yml'):
            return issues
            
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Check for running as root
                if re.search(r'USER\s+root', line, re.IGNORECASE):
                    issues.append(SecurityIssue(
                        severity="HIGH",
                        category="Docker Security",
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_num=line_num,
                        description="Container running as root user",
                        recommendation="Use non-root user (USER appuser)",
                        evidence=line.strip()
                    ))
                
                # Check for sudo without password
                if 'NOPASSWD:ALL' in line:
                    issues.append(SecurityIssue(
                        severity="CRITICAL",
                        category="Docker Security",
                        file_path=str(file_path.relative_to(self.root_path)),
                        line_num=line_num,
                        description="Sudo without password in container",
                        recommendation="Remove sudo access or require password",
                        evidence=line.strip()
                    ))
                    
        except Exception as e:
            print(f"⚠️ Error scanning Docker security in {file_path}: {e}")
            
        return issues
    
    def check_configuration_security(self) -> List[SecurityIssue]:
        """Check configuration security"""
        issues = []
        
        # Check if .env file exists and is properly configured
        env_file = self.root_path / '.env'
        if not env_file.exists():
            issues.append(SecurityIssue(
                severity="HIGH",
                category="Configuration",
                file_path=".env",
                line_num=0,
                description=".env file missing - using defaults or hardcoded values",
                recommendation="Create .env file from env.secure.template",
                evidence="File not found"
            ))
        
        # Check if secure config is imported
        config_imports = []
        for py_file in self.root_path.rglob('*.py'):
            if self.should_scan_file(py_file):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if 'from iskala_basis.config.secure_config import' in content:
                        config_imports.append(py_file)
                except:
                    continue
        
        if len(config_imports) == 0:
            issues.append(SecurityIssue(
                severity="HIGH",
                category="Configuration", 
                file_path="various",
                line_num=0,
                description="Secure configuration not imported in any Python files",
                recommendation="Import and use secure_config in all services",
                evidence="No imports found"
            ))
        
        return issues
    
    def scan_all_files(self) -> Dict[str, List[SecurityIssue]]:
        """Scan all files in the project"""
        all_issues = {}
        
        print(f"{BLUE}🔍 Scanning ISKALA codebase for security issues...{NC}")
        
        for file_path in self.root_path.rglob('*'):
            if file_path.is_file() and self.should_scan_file(file_path):
                self.stats["files_scanned"] += 1
                file_issues = []
                
                # Scan for different types of issues
                file_issues.extend(self.scan_hardcoded_secrets(file_path))
                file_issues.extend(self.scan_api_security(file_path))
                file_issues.extend(self.scan_docker_security(file_path))
                
                if file_issues:
                    all_issues[str(file_path.relative_to(self.root_path))] = file_issues
                    self.issues.extend(file_issues)
        
        # Add configuration checks
        config_issues = self.check_configuration_security()
        if config_issues:
            all_issues["configuration"] = config_issues
            self.issues.extend(config_issues)
        
        # Update stats
        for issue in self.issues:
            if issue.severity == "CRITICAL":
                self.stats["critical_issues"] += 1
            elif issue.severity == "HIGH":
                self.stats["high_issues"] += 1
            else:
                self.stats["medium_issues"] += 1
        
        return all_issues
    
    def generate_report(self, level: str = "all") -> str:
        """Generate security report"""
        report = f"""
{PURPLE}🔐 ISKALA SECURITY SCAN REPORT{NC}
{'=' * 50}
Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Files Scanned: {self.stats['files_scanned']}

{RED}📊 ISSUE SUMMARY:{NC}
Critical Issues: {self.stats['critical_issues']}
High Issues: {self.stats['high_issues']}  
Medium Issues: {self.stats['medium_issues']}
Hardcoded Secrets: {self.stats['hardcoded_secrets']}

"""
        
        # Filter issues by level
        if level == "critical":
            filtered_issues = [i for i in self.issues if i.severity == "CRITICAL"]
        elif level == "high":
            filtered_issues = [i for i in self.issues if i.severity in ["CRITICAL", "HIGH"]]
        else:
            filtered_issues = self.issues
        
        if filtered_issues:
            report += f"{RED}🚨 SECURITY ISSUES FOUND:{NC}\n"
            report += "=" * 50 + "\n\n"
            
            for issue in filtered_issues:
                report += str(issue) + "\n"
        else:
            report += f"{GREEN}✅ NO SECURITY ISSUES FOUND{NC}\n"
        
        return report
    
    def get_exit_code(self, level: str = "critical") -> int:
        """Get appropriate exit code based on issues found"""
        if level == "critical" and self.stats["critical_issues"] > 0:
            return 1
        elif level == "high" and (self.stats["critical_issues"] > 0 or self.stats["high_issues"] > 0):
            return 1
        elif level == "all" and len(self.issues) > 0:
            return 1
        return 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ISKALA Security Scanner")
    parser.add_argument("--level", choices=["critical", "high", "all"], 
                       default="critical", help="Security scan level")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--fix", action="store_true", 
                       help="Attempt to fix some issues automatically")
    
    args = parser.parse_args()
    
    # Initialize scanner
    root_path = Path(__file__).parent.parent
    scanner = ISKALASecurityScanner(root_path)
    
    # Run scan
    print(f"{PURPLE}🔐 ISKALA Security Scanner Starting...{NC}")
    print(f"Scan Level: {args.level}")
    print(f"Root Path: {root_path}")
    print()
    
    all_issues = scanner.scan_all_files()
    
    # Generate and display report
    report = scanner.generate_report(args.level)
    print(report)
    
    # Save report if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📁 Report saved to: {args.output}")
    
    # Security recommendations
    if scanner.stats["critical_issues"] > 0:
        print(f"{RED}🚨 IMMEDIATE ACTION REQUIRED:{NC}")
        print("1. Fix all CRITICAL issues before deployment")
        print("2. Rotate any exposed secrets immediately")
        print("3. Review access logs for potential compromise")
        print()
    
    if scanner.stats["hardcoded_secrets"] > 0:
        print(f"{YELLOW}💡 SECRET MANAGEMENT:{NC}")
        print("1. Move all secrets to .env file")
        print("2. Use secure_config.py for configuration")
        print("3. Add .env to .gitignore")
        print()
    
    # Exit with appropriate code
    exit_code = scanner.get_exit_code(args.level)
    if exit_code == 0:
        print(f"{GREEN}✅ Security scan passed!{NC}")
    else:
        print(f"{RED}❌ Security scan failed - fix issues before proceeding{NC}")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 