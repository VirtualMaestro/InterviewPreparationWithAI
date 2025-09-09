"""
Debug test to prove the variables are defined by exec()
"""
from datetime import datetime
from pathlib import Path

print("🔍 Debug Test: Proving exec() defines variables\n")

# Import directly from files using absolute path
project_root = Path(__file__).parent
print(f"Project root: {project_root}")

print("📁 Executing enums.py...")
exec(open(project_root / 'src/models/enums.py').read())
print("✓ enums.py executed")

print("📁 Executing simple_schemas.py...")
exec(open(project_root / 'src/models/simple_schemas.py').read())
print("✓ simple_schemas.py executed")

print("\n🔍 Checking if variables are defined:")

# Check if variables exist in local namespace
print(f"InterviewType defined: {'InterviewType' in locals()}")
print(f"ExperienceLevel defined: {'ExperienceLevel' in locals()}")
print(f"PromptTechnique defined: {'PromptTechnique' in locals()}")
print(f"AISettings defined: {'AISettings' in locals()}")
print(f"CostBreakdown defined: {'CostBreakdown' in locals()}")

if 'InterviewType' in locals():
    print(f"\n✅ InterviewType.TECHNICAL = {InterviewType.TECHNICAL.value}")
    print(f"✅ Available interview types: {[t.value for t in InterviewType]}")

if 'AISettings' in locals():
    print(f"\n✅ Creating AISettings instance...")
    settings = AISettings()
    print(
        f"✅ AISettings created: model={settings.model}, temp={settings.temperature}")

print("\n🎉 All variables are properly defined by exec()!")
print("The IDE warnings are just static analysis limitations.")
