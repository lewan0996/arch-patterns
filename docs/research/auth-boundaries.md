# Authentication boundaries and token audiences

Research for [Investigate authentication boundaries and token audiences](https://github.com/lewan0996/arch-patterns/issues/3). Checked 2026-09-19. This report establishes constraints and alternatives; it selects no catalog policy or identity provider.

## Separate the responsibilities

Authentication establishes an identity; authorization decides whether an operation is permitted. OpenID Connect authenticates users to a client and issues an ID token whose audience includes that client's identifier. An API access token serves a different purpose: granting access to protected resources. An ID token is therefore not interchangeable with an API access token. [OpenID Connect Core, sections 1–2](https://openid.net/specs/openid-connect-core-1_0.html#IDToken), [ASP.NET Core JWT bearer guidance](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-jwt-bearer-authentication?view=aspnetcore-10.0).

A bearer credential authorizes whoever possesses it; JWT describes a token format, not proof of possession. TLS protects transport, while theft from logs, storage, or a compromised component remains relevant. Audience restrictions limit where a stolen token works. [RFC 6750, sections 1.2 and 5](https://www.rfc-editor.org/rfc/rfc6750.html#section-5).

A valid token does not establish permission to edit a particular order or access another tenant's data. Resource authorization may need a loaded business object and a policy evaluated against the authenticated principal. ASP.NET Core exposes this through `IAuthorizationService`; an endpoint's authentication requirement alone cannot evaluate object ownership. [Resource-based authorization](https://learn.microsoft.com/en-us/aspnet/core/security/authorization/resource-based?view=aspnetcore-10.0).

## Browser, BFF, gateway, and service boundaries

| Composition | Credentials and boundary | Remaining concern |
| --- | --- | --- |
| Browser calls API with OAuth bearer tokens | Browser is a public OAuth client; Authorization Code with PKCE obtains API tokens | Malicious JavaScript can steal/use credentials; public clients cannot keep a client secret |
| Browser calls BFF | Confidential BFF performs OAuth and holds tokens; browser uses a session cookie | CSRF protection and secure cookie configuration; XSS can still make authenticated requests |
| Either path includes gateway | Proxy can apply authentication and route authorization before forwarding | Identity propagation and backend trust still require explicit configuration |

The first two rows follow [RFC 10017, sections 5–6](https://www.rfc-editor.org/rfc/rfc10017.html#section-6); the third follows [YARP authentication and authorization](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/authn-authz?view=aspnetcore-10.0). RFC 10017 was published as a Best Current Practice in August 2026; older browser-app Internet-Drafts are superseded. Its BFF pattern keeps access and refresh tokens away from browser JavaScript but cannot prevent malicious scripts from acting through the user's active browser session. A token-mediating backend, which releases access tokens to JavaScript, has different exposure and should not be conflated with a BFF.

A same-origin frontend and API can instead maintain a server session using cookies, optionally established through OIDC login, without browser-held OAuth access tokens. RFC 10017 explicitly leaves this application model outside its OAuth-client scope. [RFC 10017, introduction](https://www.rfc-editor.org/rfc/rfc10017.html#section-1).

YARP explicitly treats proxy and destination authentication as separate operations. Forwarded bearer tokens can be validated at the destination; a proxy-authenticated identity is not automatically recreated there. Cookie forwarding also requires deliberate compatibility. Consequently, “authentication at the gateway” is incomplete as a trust model: specify whether services validate end-user tokens, accept a protected proxy-issued assertion, or use another authenticated channel. A proxy assertion design additionally needs protection against bypass and forged identity headers. These are architectural implications of YARP's separation, not automatic framework behavior. [YARP authentication and authorization](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/yarp/authn-authz?view=aspnetcore-10.0).

For JWT access tokens, the receiving API must validate signature, issuer, audience, and expiration. This establishes acceptable credentials; it still needs authorization policies. [ASP.NET Core JWT bearer guidance](https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-jwt-bearer-authentication?view=aspnetcore-10.0).

## Audiences follow resource boundaries

JWT `aud` identifies intended recipients. It can contain one value or several; a recipient that does not identify itself in the claim must reject the token. It is not inherently the frontend, the user, a permission, or the name of a deployment. [RFC 7519, section 4.1.3](https://www.rfc-editor.org/rfc/rfc7519.html#section-4.1.3).

OAuth resource indicators identify the API or resource for which access is requested; authorization servers can map these indicators to audience values. Scopes describe requested access, whereas resource indicators say where it applies. Providers must support the relevant mechanisms for a proposed composition to work. [RFC 8707, section 2](https://www.rfc-editor.org/rfc/rfc8707.html#section-2).

**Architectural inference:** one logical API implemented by several services can share a resource identity; independently protected APIs can use separate audiences. Neither one audience per process nor one audience per modular-monolith module follows from these standards. A single shared audience, a token with multiple audiences, and several separately acquired tokens are distinct designs. Broad acceptance reduces isolation: audience restriction cannot prevent replay between recipients that intentionally accept the same token. Narrower resource boundaries constrain leakage but require token acquisition/management for those boundaries. [RFC 9700, section 4.10.2](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.10.2).

## Downstream calls and machine identities

A service receiving a token for itself cannot assume another API accepts it. RFC 8693 defines token exchange, including subject and actor concepts, allowing acquisition of a token appropriate for a downstream resource. Delegation preserves an actor acting for a subject; impersonation has different identity semantics. Exchange availability and allowed subjects, targets, and scopes remain authorization-server policy. [RFC 8693, sections 1–2](https://www.rfc-editor.org/rfc/rfc8693.html#section-1).

Provider-specific behavior matters: Microsoft Entra's on-behalf-of flow exchanges an incoming token for a downstream token using delegated user permissions. It supports user principals, not app-only principals, and requires the incoming audience to identify the receiving middle tier. This is a concrete option, not a universal OAuth capability. [Microsoft identity platform OBO flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow).

Background jobs and services acting on their own authority use application identities. OAuth client credentials supports confidential clients accessing resources under their control or prearranged authorization. It does not by itself preserve an originating user's authority. [RFC 6749, section 4.4](https://www.rfc-editor.org/rfc/rfc6749.html#section-4.4). Credential provisioning, workload identity, and sender-constrained tokens are further implementation choices; RFC 9700 discusses sender constraints as protection against stolen-token replay. [RFC 9700, section 4.10.1](https://www.rfc-editor.org/rfc/rfc9700.html#section-4.10.1).

## Questions now precise enough for decision tickets

- Which browser credential profiles will the catalog support: direct OAuth, same-origin API sessions, BFF sessions, or also token mediation?
- What defines a protected resource boundary, and when is a shared audience acceptable versus separate tokens for separate resources?
- For each gateway composition, how do services authenticate the caller, prevent bypass, and receive trustworthy identity context?
- Which downstream calls preserve user authority, and which use application authority? What provider capabilities must each recipe declare?
- Where do tenant, object, and operation authorization rules run across HTTP endpoints and in-process module calls?

These decisions require a threat model and supported-provider scope. No implementation or runtime security verification was performed; this is source-checked planning research.
