"""API routes for Animagine Prompt Node"""

import json
from aiohttp import web
from server import PromptServer
from .animagine_node import AnimaginePromptNode
from .logger import logger

# Global instance for API calls
_animagine_instance = None

def get_animagine_instance():
    """Get or create AnimaginePromptNode instance for API calls"""
    global _animagine_instance
    if _animagine_instance is None:
        _animagine_instance = AnimaginePromptNode()
    return _animagine_instance

async def reload_csv_endpoint(request):
    """
    Endpoint to reload CSV files
    
    POST /animagine/reload_csv
    Body: {"csv_path": "path/to/file.csv"}
    """
    try:
        # Get request data
        data = await request.json()
        csv_path = data.get('csv_path')
        
        if not csv_path:
            return web.json_response({
                'success': False,
                'error': 'csv_path is required'
            }, status=400)
        
        # Get node instance and reload CSV
        animagine_node = get_animagine_instance()
        result = animagine_node.reload_csv(csv_path)
        
        logger.logger.info(f"CSV reload API call: {csv_path} - Success: {result['success']}")
        
        # Return result
        status_code = 200 if result['success'] else 400
        return web.json_response(result, status=status_code)
        
    except json.JSONDecodeError:
        return web.json_response({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
        
    except Exception as e:
        logger.log_error(e, "CSV Reload API", {"request_data": str(data) if 'data' in locals() else None})
        return web.json_response({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)

def define_routes():
    """
    Define API routes using PromptServer.instance.routes
    """
    @PromptServer.instance.routes.post('/animagine/reload_csv')
    async def reload_csv_route(request):
        return await reload_csv_endpoint(request)
    
    logger.logger.info("Registered API routes for Animagine Prompt: /animagine/reload_csv")