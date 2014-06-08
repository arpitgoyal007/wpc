import re
import hmac

COOKIE_USERINFO_SECRET = "userinfosecret"
COOKIE_DEFAULT_SECRET = "defaultsecret"

def formatCookie(cookie):
	cookieDict = {}
	try:
		cookieList = cookie.split(":")
		for c in cookieList:
			cVals = c.split("=")
			cookieDict[cVals[0]] = cVals[1]
	except:
		cookieDict = {}
	return cookieDict

def hashCookieVal(secret, cookieVal):
	return hmac.new(secret, cookieVal).hexdigest()

def findCookieSecret(cookieName):
	if cookieName == "userinfo":
		secret = COOKIE_USERINFO_SECRET
	else:
		secret = COOKIE_DEFAULT_SECRET
	return secret

def secureCookieVal(cookieName, cookieVal):
	secret = findCookieSecret(cookieName)
	return "%s|%s" % (cookieVal, hashCookieVal(secret, cookieVal))

def checkSecureCookieVal(cookieName, secureCookieVal):
	secret = findCookieSecret(cookieName)
	secureCookieValList = secureCookieVal.split('|')
	if len(secureCookieValList) > 1:
		cookieVal = secureCookieValList[0]
		cookieValHash = secureCookieValList[1]
		return hashCookieVal(secret, cookieVal) == cookieValHash

