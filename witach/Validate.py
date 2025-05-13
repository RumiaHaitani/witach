class Validate:
    @staticmethod
    def required_params(data:dict, params:list):
        errors = {}
        for param in params:
            if not param in data or not data[param]:
                errors[param] = f"Параметр {param} не передан"
        
        return {
            "status": True if errors == {} else False,
            "errors":errors
        }
                
        





    


