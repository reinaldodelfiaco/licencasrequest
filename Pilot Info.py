from bs4 import BeautifulSoup
import requests
import datetime


class Habilitation:
    def __init__(self, typ: str, exp_date: datetime.date, function: str, situation: str):
        """
        Inicializa uma instância de objeto tipo Habilitation

        :param typ: str contendo o tipo de habilitação
        :param exp_date: objeto datetime.date contendo a data de validade da habilitação
        :param function: str contendo a função que o piloto está habilitado a exercer
        :param situation: str contendo a situação da habilitação
        """
        self.habilitationType = typ
        self.habilitationExpirationDate = exp_date
        self.habilitationFunction = function
        self.habilitationSituation = situation
        self.habilitationExpired = datetime.date.today() > exp_date

    def __str__(self):
        """
        :return: str formatada contendo as informações de tipo, função, situação, se a habilitação está vencida ou não,
                e data de validade da habilitação.
        """
        return (f'Tipo: {self.habilitationType}\n' +
                f'Função: {self.habilitationFunction}\n' +
                f'Situação: {self.habilitationSituation}\n' +
                f'Vencida: {"Sim" if self.habilitationExpired else "Não"}\n' +
                f'Validade: {self.habilitationExpirationDate.strftime("%d/%m/%Y")}\n')


class License:
    def __init__(self, typ: str, expedition: datetime.date, number: str, situation: str):
        """
        Inicializa uma instância do objeto License

        :param typ: str contendo o tipo de licença
        :param expedition: objeto datetime.date contendo a data de expedição da licença
        :param number: str contendo o número da licença
        :param situation: str contendo a situação da licença
        """
        self.licenseType = typ
        self.licenseExpeditionDate = expedition
        self.licenseNumber = number
        self.licenseSituation = situation

    def __str__(self):
        """
        :return: str formatada contendo o tipo, o número, a data de expedição e a situação da licença.
        """
        return (f'Tipo de licença: {self.licenseType}\n' +
                f'Número:{self.licenseNumber}\n' +
                f'Data de expedição: {self.licenseExpeditionDate.strftime("%d/%m/%Y")}\n' +
                f'Situação: {self.licenseSituation}\n')


class HC:
    def __init__(self, clas: str, exp_date: datetime.date, clinic: str, obs: str):
        """
        Inicializa uma instância do objeto HC.

        :param clas: str contendo a classe do certificado médico aeronáutico
        :param exp_date: objeto datetime.date contendo a data de validade do certificado médico aeronáutico
        :param clinic: str contendo o órgão expeditor do certificado médico aeronéutico
        :param obs: str contendo as observações feitas pelo órgão expeditor
        """
        self.certificateClass = clas
        self.certificateExpirationDate = exp_date
        self.certificateBy = clinic
        self.certificateObs = obs
        self.certificateExpired = datetime.date.today() > exp_date
    
    def __str__(self):
        return (f'Classe: {self.certificateClass}\n' +
                f'Órgão expeditor: {self.certificateBy}\n' +
                f'Observações: {self.certificateObs}\n' +
                f'Vencido: {"Sim" if self.certificateExpired else "Não"}\n' +
                f'Validade: {self.certificateExpirationDate.strftime("%d/%m/%Y")}\n')


class Pilot:
    def getsoup(self, canac, cpf):
        payload = {
            'txtCodAnac': '',
            'IDIOMA': 'P',
            'txcoddac': canac,
            # CPF deve ser do tipo str e estar formatado como "NNN.NNN.NNN-NN"
            'txCPF': cpf,
            'DtNasc': '',
            'enviar': 'enviar',
            'erroTabela': ''
            }
        url = 'https://sistemas.anac.gov.br/consultadelicencas/'
        post_request = requests.post(url, data=payload, verify=False)
        return BeautifulSoup(post_request.text, 'html.parser')

    def __init__(self, canac, cpf):
        soup = self.getsoup(canac, cpf)
        tables = soup.find_all('table')

        pilot_data = tables[7].find_all('td')
        abilities_table = tables[9].find_all('td')
        licenses_table = tables[10].find_all('td')
        hc_table = tables[11].find_all('td')

        self.UpdateTime = datetime.datetime.strptime(tables[16].find_all('td')[0].string[21:], '%d/%m/%Y %H:%M:%S')
        del(soup, tables)

        self.pilotHabilitations = []
        self.pilotLicenses = []
        self.pilotHCs = []

        self.pilotName = pilot_data[3].string.title()
        self.pilotDOB = datetime.date(int(pilot_data[5].string[-4:]), int(pilot_data[5].string[3:5]),
                                      int(pilot_data[5].string[0:2]))
        self.pilotCANAC = pilot_data[7].string
        self.pilotEmployer = pilot_data[9].string
        self.pilotBloodType = hc_table[-1].string.lstrip().rstrip()[7:]
        self.pilotObs = ''
        
        for obs in pilot_data[11].text.split('\r\n'):
            if obs.lstrip().rstrip() != '' and '$' not in obs:
                self.pilotObs += f'{obs.lstrip().rstrip()}, '
            elif '$' in obs:
                break
        if self.pilotObs[-2:] == ', ':
            self.pilotObs = self.pilotObs[:-2]

        for i in range(((len(abilities_table) - 5) // 4)):
            typ = abilities_table[(5 + 4 * i)].string
            ed = abilities_table[(6 + 4 * i)].string
            expires = datetime.date(int(ed[-4:]), int(ed[3:5]), int(ed[:2]))
            function = abilities_table[(7 + 4 * i)].string
            situation = abilities_table[(8 + 4 * i)].string
            self.pilotHabilitations.append(Habilitation(typ, expires, function, situation))

        for i in range(((len(licenses_table) - 5) // 4)):
            lic = licenses_table[(5 + 4 * i)].string
            ed = licenses_table[(6 + 4 * i)].string
            exp_date = datetime.date(int(ed[-4:]), int(ed[3:5]), int(ed[:2]))
            num = licenses_table[(7 + 4 * i)].string
            situation = licenses_table[(8 + 4 * i)].string
            self.pilotLicenses.append(License(lic, exp_date, num, situation))

        for i in range(((len(hc_table) - 5) // 4)):
            clas = hc_table[(5 + 4 * i)].string
            ed = hc_table[(6 + 4 * i)].string
            exp_date = datetime.date(int(ed[-4:]), int(ed[3:5]), int(ed[:2]))
            clinic = hc_table[(7 + 4 * i)].string
            obs = hc_table[(8 + 4 * i)].string.lstrip().rstrip()

            self.pilotHCs.append(HC(clas, exp_date, clinic, obs))

    def __str__(self):
        """
        :return: str contendo um extrato das informações pessoais do piloto, seus certificados médicos aeronáuticos,
                Habilitações e Licenças que possui.
        """
        string = '================ Informações pessoais ================\n'
        string += f'Nome: {self.pilotName}\n'
        string += f'Data de nascimento: {self.pilotDOB.strftime("%d/%m/%Y")}\n'
        string += f'Grupo sanguíneo: {self.pilotBloodType}\n\n'
        string += f'Código ANAC: {self.pilotCANAC}\n'
        string += f'Empresa: {self.pilotEmployer}\n\n'
        string += f'Observações: {self.pilotObs}\n\n'
        string += '========== Certificados Médico Aeronáutico ===========\n'
        if len(self.pilotHCs) == 0:
            string += '\nNenhum certificado médico disponível\n\n'
        else:
            for index in range(len(self.pilotHCs)):
                string += str(self.pilotHCs[index])
                if index < (len(self.pilotHCs) - 1):
                    string += '------------------------------------------------------\n\n'
                else:
                    string += '\n'

        string += '==================== Habilitações ====================\n'
        if len(self.pilotHabilitations) == 0:
            string += '\nNenhuma habilitação disponível\n\n'
        else:
            for index in range(len(self.pilotHabilitations)):
                string += str(self.pilotHabilitations[index])
                if index < (len(self.pilotHabilitations) - 1):
                    string += '------------------------------------------------------\n\n'
                else:
                    string += '\n'

        string += '====================== Licenças ======================\n'
        if len(self.pilotLicenses) == 0:
            string += '\nNenhuma licença disponível\n\n'
        else:
            for index in range(len(self.pilotLicenses)):
                string += str(self.pilotLicenses[index])
                if index < (len(self.pilotLicenses) - 1):
                    string += '------------------------------------------------------\n\n'
                else:
                    string += '\n'
        return string


def get_pilot_info(canac, cpf):
    """
    :param canac: Código ANAC do piloto a ser pesquisado. (Tipo int ou tipo str)
    :param cpf: String contendo o CPF do piloto a ser pesquisada. (Tipo int ou tipo str)
                (Quando do tipo str, pode ser usado o formato NNN.NNN.NNN-NN ou apenas os números)
    :return: Retorna uma instância do objeto tipo Pilot contendo todas as informações disponíveis no site de consultas
            da ANAC.
    """
    pilot = Pilot(str(canac), str(cpf))
    return pilot

print(get_pilot_info("canac", "cpf"))