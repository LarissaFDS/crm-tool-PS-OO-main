import re
from datetime import datetime

class ValidationError(Exception):
    pass

class Validators:
    @staticmethod
    def validate_name(name):
        if not name or not name.strip():
            raise ValidationError("Nome não pode estar vazio")
        
        name = name.strip()
        
        if not re.match(r"^[A-Za-zÀ-ÿ\s]+$", name): #pra permitir qualquer letra, acentuada ou nao, maiuscula ou minuscula e o + é falando 1 ou mais
            raise ValidationError("Nome deve conter apenas letras")
        
        if len(name) < 2:
            raise ValidationError("Nome deve ter pelo menos 2 caracteres")
        
        return name
    
    @staticmethod
    def validate_email(email):
        if not email or not email.strip():
            raise ValidationError("Email não pode estar vazio")
        
        email = email.strip().lower()
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Formato de email inválido")
        
        return email
    
    @staticmethod
    def validate_phone(phone):
        if not phone or not phone.strip():
            raise ValidationError("Telefone não pode estar vazio")
        
        phone = phone.strip()
        
        digits_only = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not digits_only.isdigit():
            raise ValidationError("Telefone deve conter apenas números")
        
        if len(digits_only) < 8:
            raise ValidationError("Telefone deve ter pelo menos 8 dígitos")
        
        return phone
    
    @staticmethod
    def validate_date(date_str, format="%d/%m/%Y"):
        if not date_str or not date_str.strip():
            raise ValidationError("Data não pode estar vazia")
        
        try:
            datetime.strptime(date_str.strip(), format)
            return date_str.strip()
        except ValueError:
            raise ValidationError(f"Data inválida. Use o formato {format}")
    
    @staticmethod
    def validate_number(value, min_val=None, max_val=None):
        if not value or not str(value).strip():
            raise ValidationError("Valor não pode estar vazio")
        
        try:
            num = int(value)
            
            if min_val is not None and num < min_val:
                raise ValidationError(f"Valor deve ser maior ou igual a {min_val}")
            
            if max_val is not None and num > max_val:
                raise ValidationError(f"Valor deve ser menor ou igual a {max_val}")
            
            return num
        except ValueError:
            raise ValidationError("Valor deve ser um número inteiro")
    
    @staticmethod
    def validate_choice(value, valid_choices, case_sensitive=False):
        if not value or not str(value).strip():
            raise ValidationError("Escolha não pode estar vazia")
        
        value = str(value).strip()
        
        if not case_sensitive:
            value_compare = value.lower()
            valid_choices_compare = [str(choice).lower() for choice in valid_choices]
        else:
            value_compare = value
            valid_choices_compare = [str(choice) for choice in valid_choices]
        
        if value_compare not in valid_choices_compare:
            raise ValidationError(
                f"Opção inválida. Escolha entre: {', '.join(map(str, valid_choices))}"
            )
            
        if not case_sensitive:
            idx = valid_choices_compare.index(value_compare)
            return valid_choices[idx]
        
        return value
    
    @staticmethod
    def validate_text(text, min_length=0, max_length=None, allow_numbers=True):
        if text is None:
            text = ""
        
        text = text.strip()
        
        if min_length > 0 and len(text) < min_length:
            raise ValidationError(f"Texto deve ter pelo menos {min_length} caracteres")
        
        if max_length and len(text) > max_length:
            raise ValidationError(f"Texto deve ter no máximo {max_length} caracteres")
        
        if not allow_numbers and any(char.isdigit() for char in text):
            raise ValidationError("Texto não pode conter números")
        
        return text


class SafeInput:
    @staticmethod
    def get_validated_input(prompt, validator_func, max_attempts=3, allow_empty=False):
        attempts = 0
        
        while attempts < max_attempts:
            try:
                value = input(prompt).strip()
                
                if allow_empty and not value:
                    return ""
                
                validated_value = validator_func(value)
                return validated_value
                
            except ValidationError as e:
                attempts += 1
                remaining = max_attempts - attempts
                
                if remaining > 0:
                    print(f"❌ Erro: {e}")
                    print(f"Tentativas restantes: {remaining}\n")
                else:
                    print(f"❌ Erro: {e}")
                    print("Número máximo de tentativas excedido.")
                    return None
            
            except KeyboardInterrupt:
                print("\n\nOperação cancelada pelo usuário.")
                return None
        
        return None
    
    @staticmethod
    def get_name(prompt="Nome: ", required=True):
        if required:
            return SafeInput.get_validated_input(prompt, Validators.validate_name)
        else:
            return SafeInput.get_validated_input(
                prompt, 
                lambda x: Validators.validate_name(x) if x else "",
                allow_empty=True
            )
    
    @staticmethod
    def get_email(prompt="Email: "):
        return SafeInput.get_validated_input(prompt, Validators.validate_email)
    
    @staticmethod
    def get_phone(prompt="Telefone: "):
        return SafeInput.get_validated_input(prompt, Validators.validate_phone)
    
    @staticmethod
    def get_date(prompt="Data (dd/mm/aaaa): "):
        return SafeInput.get_validated_input(prompt, Validators.validate_date)
    
    @staticmethod
    def get_number(prompt="Número: ", min_val=None, max_val=None):
        return SafeInput.get_validated_input(
            prompt,
            lambda x: Validators.validate_number(x, min_val, max_val)
        )
    
    @staticmethod
    def get_choice(prompt, valid_choices, case_sensitive=False):
        return SafeInput.get_validated_input(
            prompt,
            lambda x: Validators.validate_choice(x, valid_choices, case_sensitive)
        )