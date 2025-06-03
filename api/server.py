from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import psutil
import platform
from datetime import datetime, UTC
import traceback
from threading import Thread
import os
import importlib
import pkgutil
from pathlib import Path
from .dependencies import set_bot
from .routes import router as api_router
from .middleware import setup_middleware
from .middleware.auth import auth_middleware
from .config import API_VERSION

logger = logging.getLogger(__name__)

class APIServer:
    def __init__(self, bot):
        self.app = FastAPI(
            title="Discord Bot API",
            description="Backend API for Growtopia Shop Bot",
            version=API_VERSION,
            docs_url=None,
            redoc_url=None,
            openapi_url=None
        )
        self.bot = bot
        self.startup_time = datetime.now(UTC)
        # Tambahkan dictionary untuk melacak modul
        self.loaded_modules = {}
        
        # Setup static files
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        # Tambahkan pemanggilan load_all_modules sebelum setup_api
        self.load_all_modules()
        self.setup_api()
        
        logger.debug(f"""
        API Server initialized:
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        Bot: {self.bot.__class__.__name__}
        FastAPI App: {self.app.__class__.__name__}
        Version: {API_VERSION}
        Python: {platform.python_version()}
        OS: {platform.platform()}
        Loaded Modules: {list(self.loaded_modules.keys())}
        User: fdygt
        """)

    def load_all_modules(self):
        """Memuat semua modul di folder api secara dinamis"""
        api_path = Path(__file__).parent
        
        logger.info(f"""
        Memulai pemuatan modul:
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        Path: {api_path}
        User: fdygt
        """)
        
        # Daftar folder yang akan di-scan
        folders_to_scan = ['routes', 'service', 'models', 'middleware', 'dependencies', 'config']
        
        for folder in folders_to_scan:
            folder_path = api_path / folder
            if not folder_path.exists():
                logger.warning(f"""
                Folder tidak ditemukan:
                Folder: {folder}
                Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                User: fdygt
                """)
                continue
                
            logger.info(f"Memuat modul dari folder: {folder}")
            
            try:
                # Memuat semua modul dalam folder
                for module_info in pkgutil.iter_modules([str(folder_path)]):
                    module_name = f"api.{folder}.{module_info.name}"
                    if module_name not in self.loaded_modules:
                        try:
                            module = importlib.import_module(module_name)
                            self.loaded_modules[module_name] = module
                            logger.info(f"""
                            Berhasil memuat modul:
                            Module: {module_name}
                            Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                            User: fdygt
                            """)
                            
                            # Jika modul memiliki router, daftarkan ke FastAPI
                            if hasattr(module, 'router'):
                                prefix = f"/api/v1/{folder}/{module_info.name}"
                                self.app.include_router(
                                    module.router,
                                    prefix=prefix,
                                    tags=[folder.capitalize()]
                                )
                                logger.info(f"""
                                Terdaftar router untuk:
                                Module: {module_name}
                                Prefix: {prefix}
                                Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                                User: fdygt
                                """)
                                
                        except Exception as e:
                            logger.error(f"""
                            Gagal memuat modul:
                            Module: {module_name}
                            Error: {str(e)}
                            Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                            User: fdygt
                            Stack Trace:
                            {traceback.format_exc()}
                            """)
                            
            except Exception as e:
                logger.error(f"""
                Gagal memindai folder:
                Folder: {folder}
                Error: {str(e)}
                Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                User: fdygt
                Stack Trace:
                {traceback.format_exc()}
                """)

    def get_system_info(self):
        """Get system information with fallbacks"""
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "percent": round(memory.percent, 2)
            }
        except:
            memory_info = {"error": "Memory stats unavailable"}
            
        try:
            disk = psutil.disk_usage('/')
            disk_info = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": round(disk.percent, 2)
            }
        except:
            disk_info = {"error": "Disk stats unavailable"}
            
        try:
            cpu_percent = round(psutil.cpu_percent(interval=0.1), 2)
        except:
            cpu_percent = 0.0
            
        return {
            "memory": memory_info,
            "disk": disk_info,
            "cpu_percent": cpu_percent
        }

    def setup_api(self):
        """Setup API routes and middleware"""
        logger.debug("Setting up API routes and middleware")
        
        try:
            # Setup CORS
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["GET", "POST", "PUT", "DELETE"],
                allow_headers=["*"],
                expose_headers=["X-Request-ID"]
            )
            
            # Add auth middleware
            self.app.middleware("http")(auth_middleware)
            
            # Set bot instance
            set_bot(self.bot)
            
            # Include routers with prefix
            self.app.include_router(
                api_router,
                prefix="/api/v1"
            )
            
            # Setup middleware and error handlers
            setup_middleware(self.app)

            # Add exception handlers
            @self.app.exception_handler(HTTPException)
            async def http_exception_handler(request: Request, exc: HTTPException):
                """Handle HTTP exceptions"""
                return JSONResponse(
                    status_code=exc.status_code,
                    content={
                        "detail": exc.detail,
                        "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                        "path": request.url.path,
                        "type": "HTTPException"
                    }
                )

            @self.app.exception_handler(Exception)
            async def general_exception_handler(request: Request, exc: Exception):
                """Handle general exceptions"""
                logger.error(f"""
                Unhandled exception:
                Path: {request.url.path}
                Error: {str(exc)}
                Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                User: fdygt
                """)
                return JSONResponse(
                    status_code=500,
                    content={
                        "detail": "Internal server error",
                        "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                        "path": request.url.path,
                        "type": "InternalServerError"
                    }
                )
            
            # Add favicon endpoint
            @self.app.get("/favicon.ico", include_in_schema=False)
            async def favicon():
                favicon_path = Path(__file__).parent / "static/favicon.ico"
                if favicon_path.exists():
                    return FileResponse(str(favicon_path))
                return JSONResponse(
                    status_code=404,
                    content={
                        "detail": "Not Found",
                        "message": "Favicon not found",
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                )
            
            # Add OpenAPI endpoint
            @self.app.get("/api/v1/openapi.json", include_in_schema=False)
            async def get_openapi_schema():
                openapi_schema = get_openapi(
                    title="Growtopia Shop Bot API",
                    version=API_VERSION,
                    description=f"""
                    Backend API for Growtopia Shop Discord Bot.
                    
                    API Version: {API_VERSION}
                    Server Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
                    
                    Authentication:
                    - All endpoints except public endpoints require authentication
                    - Use Bearer token authentication
                    - Get token from /api/v1/auth/token endpoint
                    """,
                    routes=self.app.routes,
                )
                return JSONResponse(openapi_schema)
            
            # Add health check endpoint
            @self.app.get("/")
            async def root(request: Request):
                uptime = datetime.now(UTC) - self.startup_time
                system_info = self.get_system_info()
                
                response_data = {
                    "status": "ok",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "version": API_VERSION,
                    "bot": {
                        "name": self.bot.user.name if self.bot.user else None,
                        "id": str(self.bot.user.id) if self.bot.user else None,
                        "startup_time": self.bot.startup_time.isoformat() if hasattr(self.bot, 'startup_time') else None,
                        "uptime": str(uptime),
                        "guilds": len(self.bot.guilds) if hasattr(self.bot, 'guilds') else 0
                    },
                    "server": {
                        "hostname": platform.node(),
                        "platform": platform.platform(),
                        "python": platform.python_version(),
                        **system_info
                    },
                    "client": {
                        "ip": request.client.host,
                        "port": request.client.port,
                        "user_agent": request.headers.get("user-agent")
                    }
                }
            
                return JSONResponse(
                    content=response_data,
                    headers={
                        "Cache-Control": "no-cache, no-store, must-revalidate",
                        "Pragma": "no-cache",
                        "Expires": "0"
                    }
                )

            # Tambahkan endpoint untuk melihat modul yang dimuat
            @self.app.get("/api/v1/debug/modules", include_in_schema=False)
            async def list_modules():
                return {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "total_modules": len(self.loaded_modules),
                    "modules": {
                        name: {
                            "file": module.__file__,
                            "has_router": hasattr(module, 'router'),
                            "doc": module.__doc__
                        } for name, module in self.loaded_modules.items()
                    }
                }

            # Add docs endpoints
            @self.app.get("/docs", include_in_schema=False)
            async def custom_swagger_ui_html():
                return get_swagger_ui_html(
                    openapi_url="/api/v1/openapi.json",
                    title=f"Bot API Documentation - {API_VERSION}",
                    swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
                    swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
                    swagger_favicon_url="/favicon.ico"
                )
            
            # Add debug routes endpoint
            @self.app.get("/api/v1/debug/routes", include_in_schema=False)
            async def list_routes(request: Request):
                routes = []
                for route in self.app.routes:
                    routes.append({
                        "path": route.path,
                        "name": route.name,
                        "methods": list(route.methods) if route.methods else None,
                        "tags": route.tags if hasattr(route, 'tags') else None,
                        "deprecated": route.deprecated if hasattr(route, 'deprecated') else False,
                        "description": route.description if hasattr(route, 'description') else None
                    })
                return {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "total_routes": len(routes),
                    "routes": sorted(routes, key=lambda x: x['path']),
                    "request": {
                        "client": request.client.host,
                        "method": request.method,
                        "url": str(request.url)
                    }
                }
                
            logger.info(f"""
            API routes and middleware setup completed:
            Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
            Total Routes: {len(self.app.routes)}
            Auth Enabled: True
            CORS Enabled: True
            Version: {API_VERSION}
            User: fdygt
            """)
            
        except Exception as e:
            logger.error(f"""
            API setup error:
            Error: {str(e)}
            Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
            User: fdygt
            Stack Trace:
            {traceback.format_exc()}
            """)
            raise

    def run(self):
        """Run API server"""
        try:
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8080,
                log_level="debug",
                access_log=True,
                reload=False,
                http="h11",
                loop="asyncio",
                timeout_keep_alive=5,
                timeout_notify=30,
                limit_concurrency=1000,
                limit_max_requests=10000,
                log_config={
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "default": {
                            "format": "%(asctime)s UTC - %(name)s - %(levelname)s - [User: fdygt]\nMessage: %(message)s",
                            "datefmt": "%Y-%m-%d %H:%M:%S"
                        }
                    },
                    "handlers": {
                        "default": {
                            "formatter": "default",
                            "class": "logging.StreamHandler",
                            "stream": "ext://sys.stdout"
                        }
                    },
                    "loggers": {
                        "uvicorn": {"handlers": ["default"], "level": "INFO"},
                        "uvicorn.error": {"level": "INFO"},
                        "uvicorn.access": {
                            "handlers": ["default"],
                            "level": "INFO",
                            "propagate": False
                        }
                    }
                }
            )
            
            server = uvicorn.Server(config)
            
            logger.info(f"""
            Starting API server:
            Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
            Host: 0.0.0.0
            Port: 8080
            Debug: True
            Version: {API_VERSION}
            User: fdygt
            """)
            
            server.run()
            
        except Exception as e:
            logger.error(f"""
            Failed to start API server:
            Error: {str(e)}
            Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
            User: fdygt
            Stack Trace:
            {traceback.format_exc()}
            """)
            raise

def create_api_server(bot) -> APIServer:
    """Create and start API server in a separate thread"""
    try:
        logger.debug(f"""
        Creating API server:
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        Bot Type: {type(bot).__name__ if bot else 'None'}
        User: fdygt
        """)

        api = APIServer(bot)
        
        # Create and start server thread
        api_thread = Thread(
            target=api.run,
            daemon=True,
            name="APIServerThread"
        )
        api_thread.start()
        
        logger.info(f"""
        API server thread started:
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        Thread ID: {api_thread.ident}
        Thread Name: {api_thread.name}
        Status: Running
        Version: {API_VERSION}
        User: fdygt
        """)
        
        return api
        
    except Exception as e:
        logger.error(f"""
        Error creating API server:
        Error: {str(e)}
        Time: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC
        User: fdygt
        Stack Trace:
        {traceback.format_exc()}
        """)
        raise

# Export api server creation function
__all__ = ["create_api_server"]