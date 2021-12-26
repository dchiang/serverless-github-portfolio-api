class GitHubParser:

    def __init__(self):
        self.languagesColors = dict()

    def setLanguagesColors(self, languagesColors):
        self.languagesColors = languagesColors

    def __getLanguageColor(self, languageName):
        return self.languagesColors[languageName]["color"]

    def __getUserProfile(self, githubUser):
        profile = dict()
        for key, value in githubUser.items():
            if key == "twitterUsername":
                value = "https://twitter.com/" + value if value else None
                profile.update({"twitterUrl": value})
            elif key != "repositories":
                profile.update({key: value})
        return profile

    def __getRepositories(self, repositoriesList):
        repositories = list()
        for element in repositoriesList:
            repository = dict()
            for key, value in element.items():
                if key == "languages":
                    languages = dict()
                    languages.update(
                        {"totalSize": element["languages"]["totalSize"]})
                    languagesList = list()
                    for repoLanguage in element["languages"]["edges"]:
                        language = dict()
                        language.update({"name": repoLanguage["node"]["name"]})
                        language.update({"size": repoLanguage["size"]})
                        language.update(
                            {"color": self.__getLanguageColor(language["name"])})
                        languagesList.append(language)
                    languages.update({"list": languagesList})
                    value = languages
                repository.update({key: value})
            repositories.append(repository)
        return repositories

    def __getReposStackLanguages(self, repositories):
        stackedLanguages = dict()
        stackedLanguages.update({"totalSize": 0})
        stackedLanguages.update({"list": list()})
        for repository in repositories:
            stackedLanguages.update(
                {
                    "totalSize": stackedLanguages["totalSize"]
                    + repository["languages"]["totalSize"]
                }
            )
            reposLanguages = repository["languages"]["list"]
            for repoLanguage in reposLanguages:
                language = dict(repoLanguage)
                updated = False
                for index in range(len(stackedLanguages["list"])):
                    stacked = stackedLanguages["list"][index]
                    if stackedLanguages["list"][index]["name"] == language["name"]:
                        stackedLanguages["list"][index]["size"] = stackedLanguages["list"][index]["size"] + \
                            language["size"]
                        updated = True
                if updated is False:
                    stackedLanguages["list"].append(language)
        return stackedLanguages

    def parseGitHubResponse(self, githubResponse):
        portfolio = dict()
        profile = self.__getUserProfile(githubResponse["user"])
        repositories = self.__getRepositories(
            githubResponse["user"]["repositories"]["nodes"]
        )
        languages = self.__getReposStackLanguages(repositories)
        portfolio.update({"profile": profile})
        portfolio.update({"repositories": repositories})
        portfolio.update({"languages": languages})
        return portfolio
