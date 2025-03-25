import requests
import os
import bs4
import re
import dataclasses


@dataclasses.dataclass
class State:
    view_state: str
    authenticity_token: str
    form_action: str

    @classmethod
    def from_response(cls, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        authenticity_token = soup.select_one(
            "form[name='studyserviceForm'] > input[name='authenticity_token']"
        ).attrs["value"]

        view_state = re.search(
            r"_flowExecutionKey=(.*)&?", str(response.request.url)
        ).group(1)

        form_action = soup.select_one("form[name='studyserviceForm']").attrs["action"]

        return cls(
            view_state=view_state,
            authenticity_token=authenticity_token,
            form_action=form_action,
        )


def main():
    USERNAME = os.environ.get("HSBO_USERNAME")
    PASSWORD = os.environ.get("HSBO_PASSWORD")
    OUTPATH = os.environ.get("HSBO_OUTPUTPATH")

    with requests.Session() as session:
        login_response = session.post(
            url="https://studonline.hs-bochum.de:443/qisserver/rds?state=user&type=1&category=auth.login",
            data={
                "asdf": USERNAME,
                "fdsa": PASSWORD,
            },
        )

        login_response.raise_for_status()

        page_res = session.get(
            "https://studonline.hs-bochum.de/qisserver/pages/cm/exa/enrollment/info/start.xhtml?_flowId=studyservice-flow&_flowExecutionKey=e1s1"
        )
        page_res.raise_for_status()

        state = State.from_response(page_res)

        page_res = session.post(
            url=f"https://studonline.hs-bochum.de{state.form_action}",
            data={
                "activePageElementId": "studyserviceForm:report_TabBtn",
                "refreshButtonClickedId": "",
                "navigationPosition": "",
                "authenticity_token": state.authenticity_token,
                "autoScroll": "0,0",
                "studyserviceForm:fieldsetPersoenlicheData:collapsiblePanelCollapsedState": "",
                "studyserviceForm:content.9": "",
                "studyserviceForm:stgStudent:collapsibleFieldsetCourseOfStudies:collapsiblePanelCollapsedState": "",
                "studyserviceForm_SUBMIT": "1",
                "javax.faces.ViewState": state.view_state,
            },
        )
        page_res.raise_for_status()

        state = State.from_response(page_res)

        mensa_card_res = session.post(
            url=f"https://studonline.hs-bochum.de{state.form_action}",
            data={
                "activePageElementId": "",
                "refreshButtonClickedId": "",
                "navigationPosition": "hisinoneMeinStudium,hisinoneStudyservice",
                "authenticity_token": state.authenticity_token,
                "autoScroll": "",
                "studyserviceForm:fieldsetPersoenlicheData:collapsiblePanelCollapsedState": "value",
                "studyserviceForm:report:outputRequests:collapsiblePanelCollapsedState": "",
                "studyserviceForm:report:reports:collapsiblePanelCollapsedState": "",
                "studyserviceForm_SUBMIT": "1",
                "javax.faces.ViewState": state.view_state,
                "javax.faces.behavior.event": "action",
                "javax.faces.partial.event": "click",
                "javax.faces.source": "studyserviceForm:report:reports:reportButtons:jobConfigurationButtons:0:jobConfigurationButtons:3:job2",
                "javax.faces.partial.ajax": "true",
                "javax.faces.partial.execute": "studyserviceForm:report:reports:reportButtons:jobConfigurationButtons:0:jobConfigurationButtons:3:job2",
                "javax.faces.partial.render": "studyserviceForm:report:reports:reportButtons:jobConfigurationButtonsOverlay studyserviceForm:report:reports:reportButtons:jobDownload studyserviceForm:messages-infobox",
                "studyserviceForm": "studyserviceForm",
            },
        )
        mensa_card_res.raise_for_status()

        link = re.search(r"""href=\"(.*?)\"""", mensa_card_res.text).group(1)
        link = link.replace("&amp;", "&")

        file_res = session.get(url=f"https://studonline.hs-bochum.de{link}")

        if OUTPATH == "-" or OUTPATH is None:
            print(file_res.content)
        else:
            with open(OUTPATH, "wb") as f:
                f.write(file_res.content)


if __name__ == "__main__":
    main()
