from .cbi_utils.session import get
from .cbi_utils.clean_and_extend_data import clean_tsd_cbi


class CBI:
    def national_accounts(self):
        main = get(
            url="https://tsd.cbi.ir/WebResource.axd?d=bO-UbQmRNrkyCtnvoI8Hw7lykeK9aEY-Ha6RpiE4wXz3LRlgIrobvpJBrVP958qZNDEFJ-Pq7SRi7FhEBGu2T2hz47fnIFlLei6B8mk8sDg3RKX6WIvWAB2a3bbpr5Qiotv1cTFa_pciVOo3w3cv3GxNXnZbAUXFN-2WFAdm-WaNtrixBwSYzVQUT0O6hMw60&t=636624960042575190",
            rep_url="https://tsd.cbi.ir/Display/ShowExcelReport.aspx?DT=0",
        )
        return clean_tsd_cbi(main.text)
