# licencasrequest
Módulo destinado a captura de informações de licenças, habilitações, certificados médicos dentre outras publicamente disponíveis.


Para obter os dados, usar as funções:

get_pilot_info("canac", "cpf")
ou
get_pilot_info_as_json("canac", "cpf")

O retorno se dá na forma de um objeto (Python/JSON) tipo Pilot. 
