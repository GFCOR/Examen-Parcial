try:
    from domain.models import Student, Evaluation
    print("Import successful")
    e = Evaluation(score=10, weight=50)
    print(f"Evaluation created: {e}")
    s = Student(id="1")
    print(f"Student created: {s}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
