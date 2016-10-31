
import tests

def validate(obj, **opts):
    test_class_name = repr(obj)+"_Test"
    test_class = getattr(tests, test_class_name)
    validator = test_class(base=obj, cheat_all_tests=True)

    for test_func in validator:
        try:
            validator.setUp()
            test_func()
            validator.tearDown()
        except Exception as e:
            validator.conditions.append( (None, str(e)) )

    # Some conditions could be duplicates, but I'm not going to dedupe
    #   that down because it's possible someone might want the number
    #   of tests that failed
    return validator.conditions

def all_ok(validator_conditions):
    return all( passed is True 
                for passed, _ in validator_conditions )
