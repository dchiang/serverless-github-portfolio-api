import boto3
from Parameter import Parameter


def getUrlParameter(parametersDict, parameter, type):
    if parametersDict and parameter in parametersDict:
        return parametersDict[parameter]
    elif type == Parameter.QUERY:
        return None
    elif type == Parameter.PATH:
        raise LookupError("400", "path parameter " + parameter + " is missing")


def getSystemManagerParameter(region, parameter):
    ssm = boto3.client("ssm", region)
    try:
        systemManagerParameter = ssm.get_parameter(Name=parameter)
        return systemManagerParameter["Parameter"]["Value"]
    except ssm.exceptions.ParameterNotFound:
        statusCode = "500"
        message = "parameter " + parameter + " not defined in ssm for region " + region
        raise LookupError(statusCode, message)
    except ssm.exceptions.InternalServerError:
        statusCode = "503"
        message = (
            "parameter " + parameter + " could not be retrieved from region " + region
        )
        raise LookupError(statusCode, message)
