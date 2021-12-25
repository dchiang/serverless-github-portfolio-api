import json
import util
import requests
from Parameter import Parameter
from GitHubParser import GitHubParser


def getLogin(parametersDict):
    parameter = "login"
    return util.getUrlParameter(parametersDict, parameter, Parameter.PATH)


def getGitHubPortfolioPAT():
    region = "us-east-2"
    parameter = "githubPortfolioPersonalAccessToken"
    return util.getSystemManagerParameter(region, parameter)


def getLanguagesAmount(parametersDict):
    default = "10"
    parameter = "languages-amount"
    languagesAmount = util.getUrlParameter(
        parametersDict, parameter, Parameter.QUERY)
    return languagesAmount if languagesAmount else default


def getReposAmount(parametersDict):
    default = "10"
    parameter = "repos-amount"
    reposAmount = util.getUrlParameter(
        parametersDict, parameter, Parameter.QUERY)
    return reposAmount if reposAmount else default


def getParameters(event):
    login = getLogin(event["pathParameters"])
    gitHubPortfolioPAT = getGitHubPortfolioPAT()
    reposAmount = getReposAmount(event["queryStringParameters"])
    languagesAmount = getLanguagesAmount(event["queryStringParameters"])
    parameters = {
        "login": login,
        "gitHubPortfolioPAT": gitHubPortfolioPAT,
        "reposAmount": reposAmount,
        "languagesAmount": languagesAmount,
    }
    return parameters


def queryGitHub(parameters):
    apiURL = "https://api.github.com"
    endpoint = apiURL + "/graphql"
    headers = {"Authorization": "bearer " + parameters["gitHubPortfolioPAT"]}
    query = {
        "query": '''query PortfolioQuery {
                user(login: "'''
        + parameters["login"]
        + """") {
                    login
                    avatarUrl
                    bio
                    email
                    name
                    location
                    twitterUsername
                    url
                    websiteUrl
                    repositories(orderBy: {field: PUSHED_AT, direction: DESC}, affiliations: OWNER, last: """
        + parameters["reposAmount"]
        + """) {
                        nodes {
                            description
                            homepageUrl
                            name
                            pushedAt
                            url
                            openGraphImageUrl
                            languages(last: """
        + parameters["languagesAmount"]
        + """) {
                                totalSize
                                edges {
                                    node {
                                        name
                                    }
                                    size
                                }
                            }
                        }
                    }
                }
            }"""
    }
    try:
        request = requests.post(endpoint, json=query, headers=headers)
        response = request.json()["data"]
        return response
    except requests.RequestException as exception:
        raise ConnectionError(
            "503", "Something went wrong while trying to get data from GitHub" + exception
        )


def lambdaResponse(statusCode, body):
    return {
        "statusCode": statusCode,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        parameters = getParameters(event)
        githubResponse = queryGitHub(parameters)
        responseParser = GitHubParser()
        response = responseParser.parseGitHubResponse(githubResponse)
        return lambdaResponse(200, response)
    except (LookupError, ConnectionError) as exception:
        statusCode, message = exception.args
        return lambdaResponse(statusCode, body={"message": message})
