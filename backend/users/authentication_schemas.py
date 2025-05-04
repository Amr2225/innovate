from drf_spectacular.extensions import OpenApiAuthenticationExtension


class FirstLoginAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Custom authentication scheme for FirstLoginAuthentication.
    """
    target_class = 'users.authentication.FirstLoginAuthentication'  # Path to your custom authentication class
    name = 'FirstLoginAuth'  # Name of the authentication scheme

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Token-based authentication using FirstLoginAuthentication',
        }
