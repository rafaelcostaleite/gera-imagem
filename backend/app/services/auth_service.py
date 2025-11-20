from ldap3 import Server, Connection, ALL, NTLM
from ldap3.core.exceptions import LDAPException
from typing import Optional, Dict
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ADAuthService:
    """Serviço de autenticação via Active Directory (LDAP)"""

    def __init__(self):
        self.server = settings.AD_SERVER
        self.domain = settings.AD_DOMAIN
        self.base_dn = settings.AD_BASE_DN
        self.use_ssl = settings.AD_USE_SSL

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, str]]:
        """
        Autentica usuário no Active Directory

        Args:
            username: Nome de usuário
            password: Senha

        Returns:
            Dict com informações do usuário se autenticado, None caso contrário
        """
        try:
            # Criar servidor LDAP
            server = Server(self.server, get_info=ALL, use_ssl=self.use_ssl)

            # Formato do usuário para AD: DOMAIN\\username
            user_dn = f"{self.domain}\\{username}"

            # Tentar conexão
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=NTLM,
                auto_bind=True
            )

            if conn.bind():
                # Buscar informações do usuário
                search_filter = f"(sAMAccountName={username})"
                conn.search(
                    search_base=self.base_dn,
                    search_filter=search_filter,
                    attributes=['cn', 'mail', 'displayName', 'sAMAccountName']
                )

                if conn.entries:
                    entry = conn.entries[0]
                    user_info = {
                        'username': str(entry.sAMAccountName) if hasattr(entry, 'sAMAccountName') else username,
                        'email': str(entry.mail) if hasattr(entry, 'mail') else f"{username}@{self.domain}",
                        'full_name': str(entry.displayName) if hasattr(entry, 'displayName') else username,
                    }

                    conn.unbind()
                    logger.info(f"Usuário {username} autenticado com sucesso")
                    return user_info
                else:
                    logger.warning(f"Usuário {username} não encontrado no AD")
                    conn.unbind()
                    return None

            logger.warning(f"Falha ao autenticar usuário {username}")
            return None

        except LDAPException as e:
            logger.error(f"Erro ao autenticar no AD: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao autenticar: {str(e)}")
            return None

    def get_user_info(self, username: str) -> Optional[Dict[str, str]]:
        """
        Busca informações de um usuário no AD (sem autenticar)

        Args:
            username: Nome de usuário

        Returns:
            Dict com informações do usuário
        """
        try:
            # Para buscar info sem senha, precisaríamos de um usuário de serviço
            # Por enquanto, retorna None
            logger.info(f"Busca de informações para usuário {username}")
            return None

        except Exception as e:
            logger.error(f"Erro ao buscar informações do usuário: {str(e)}")
            return None


# Instância global do serviço
ad_auth_service = ADAuthService()
