from aiogram import Router
from .start import router as start_router
from .services import router as services_router
from .balance import router as balance_router
from .profile import router as profile_router
from .help import router as help_router
from .admin import router as admin_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(services_router)
main_router.include_router(balance_router)
main_router.include_router(profile_router)
main_router.include_router(help_router)
main_router.include_router(admin_router)
