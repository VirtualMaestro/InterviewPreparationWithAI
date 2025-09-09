"""
Prove that static analysis can't understand exec() but code works fine
"""

from pathlib import Path
print("🧪 Demonstrating static analysis limitation\n")

# This will show a warning in IDE but works perfectly
exec("my_variable = 'Hello from exec!'")

# IDE will show "undefined variable" warning here, but it works:
print(f"✅ Variable from exec(): {my_variable}")  # type: ignore

# Same with our models:

project_root = Path(__file__).parent
exec(open(project_root / 'src/models/enums.py').read())

# IDE shows warning, but this works perfectly:
# type: ignore
print(f"✅ InterviewType from exec(): {InterviewType.TECHNICAL.value}")

print("\n🎯 Conclusion:")
print("- The code WORKS perfectly ✅")
print("- The IDE warnings are just static analysis limitations ⚠️")
print("- Use '# type: ignore' to suppress warnings if needed")
