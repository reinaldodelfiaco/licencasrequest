from bs4 import BeautifulSoup
import json
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
    @staticmethod
    def get_soup(canac, cpf):
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
        post_request = requests.post(url, data=payload, verify=True)
        return BeautifulSoup(post_request.text, 'html.parser')

    def __init__(self, canac, cpf):
        soup = self.get_soup(canac, cpf)
        tables = soup.find_all('table')

        pilot_data = tables[7].find_all('td')
        abilities_table = tables[9].find_all('td')
        licenses_table = tables[10].find_all('td')
        hc_table = tables[11].find_all('td')

        self.UpdateTime = datetime.datetime.strptime(tables[16].find_all('td')[0].string[21:], '%d/%m/%Y %H:%M:%S')
        self.pilotName = pilot_data[3].string.strip().title()
        self.pilotCANAC = pilot_data[7].string
        self.pilotDOB = datetime.date(int(pilot_data[5].string[-4:]), int(pilot_data[5].string[3:5]),
                                      int(pilot_data[5].string[0:2]))
        self.pilotBloodType = hc_table[-1].string.strip()[7:]
        self.pilotEmployer = pilot_data[9].string

        self.pilotObs = []
        self.pilotHabilitations = []
        self.pilotLicenses = []
        self.pilotHCs = []

        for obs in pilot_data[11].text.split('\r\n'):
            if obs.strip() != '' and '$' not in obs:
                self.pilotObs.append(obs.strip().strip('.'))
            elif '$' in obs:
                break

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
            obs = hc_table[(8 + 4 * i)].string.strip().strip('.')

            self.pilotHCs.append(HC(clas, exp_date, clinic, obs))

    def serialize(self):
        """
                Função recebe uma instância de objeto tipo Pilot e converte as listas de certificados de saúde (HCs),
                licenças (Licenses) e habilitações (Habilitations) para um formato serializado, pronto para conversão
                para JSON.
                :param self: instância de objeto Pilot
                """
        index: int
        for index in range(len(self.pilotHCs)):
            self.pilotHCs[index] = self.pilotHCs[index].__dict__

        for index in range(len(self.pilotLicenses)):
            self.pilotLicenses[index] = self.pilotLicenses[index].__dict__

        for index in range(len(self.pilotHabilitations)):
            self.pilotHabilitations[index] = self.pilotHabilitations[index].__dict__

        return self.__dict__

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
        string += '==================== Observações =====================\n'
        if len(self.pilotObs) == 0:
            string += '\nNenhuma observação disponível\n\n'
        else:
            for index in range(len(self.pilotObs)):
                string += f'{self.pilotObs[index]}\n'
                if index == (len(self.pilotObs) - 1):
                    string += '\n'
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
    return Pilot(str(canac), str(cpf))


def get_pilot_info_as_json(canac, cpf):
    """
    Função recebe as informações de CANAC e CPF do piloto a ser pesquisado, efetua uma pesquisa no site de consultas
    da ANAC e retorna um objeto tipo Pilot com todas as informações publicamentes disponíveis em formato JSON.
    :param canac: string contendo o Código ANAC do piloto a ser pesquisado.
    :param cpf: string contendo o CPF do piloto a ser pesquisado.
    :return: objeto tipo Pilot em formato JSON.
    """
    def default_serializer_behaviour(instance):
        if isinstance(instance, (datetime.date, datetime.datetime)):
            return instance.isoformat()

    return json.dumps(get_pilot_info(canac, cpf).serialize(),
                      indent=4, default=default_serializer_behaviour, ensure_ascii=False)
