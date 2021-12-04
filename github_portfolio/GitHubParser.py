class GitHubParser:
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
                    languages.update({"totalSize": element["languages"]["totalSize"]})
                    languagesList = dict()
                    for repoLanguage in element["languages"]["edges"]:
                        languagesList.update(
                            {repoLanguage["node"]["name"]: repoLanguage["size"]}
                        )
                    languages.update({"list": languagesList})
                    key = "languages"
                    value = languages
                repository.update({key: value})
            repositories.append(repository)
        return repositories

    def __getReposStackLanguages(self, repositories):
        stackedLanguages = dict()
        stackedLanguages.update({"list": {}})
        stackedLanguages.update({"totalSize": 0})
        for repository in repositories:
            stackedLanguages.update(
                {
                    "totalSize": stackedLanguages["totalSize"]
                    + repository["languages"]["totalSize"]
                }
            )
            reposLanguages = repository["languages"]["list"]
            for key, value in reposLanguages.items():
                if key in stackedLanguages["list"].keys():
                    stackedLanguages["list"].update(
                        {key: stackedLanguages["list"][key] + value}
                    )
                else:
                    stackedLanguages["list"].update({key: value})
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
