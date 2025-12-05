#!/usr/bin/env python3
"""
Simple HTTP server to serve the generated XMLTV EPG file and M3U playlist.
This allows external applications like Jellyfin to access the EPG and playlist via HTTP.
"""

import os
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler

logger = logging.getLogger(__name__)


class EPGRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for serving EPG and M3U files."""
    
    epg_file_path = None
    m3u_file_path = None
    
    def do_GET(self):
        """Handle GET requests for the EPG and M3U files."""
        # EPG file endpoints
        if self.path in ['/', '/guide.xml', '/epg.xml']:
            self._serve_file(self.epg_file_path, 'application/xml', 'EPG')
        # M3U playlist endpoints  
        elif self.path in ['/channels.m3u', '/playlist.m3u', '/lineup.m3u']:
            self._serve_file(self.m3u_file_path, 'audio/x-mpegurl', 'M3U playlist')
        # Health check endpoint
        elif self.path == '/health':
            self._serve_health_check()
        # Status endpoint
        elif self.path == '/status':
            self._serve_status()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')
    
    def _serve_file(self, file_path, content_type, file_type):
        """Serve a file with appropriate content type."""
        try:
            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'max-age=300')  # Cache for 5 minutes
                self.end_headers()
                self.wfile.write(content)
                logger.info("Served %s file: %s", file_type, self.path)
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'{file_type} file not found'.encode())
                logger.warning("%s file not found: %s", file_type, file_path)
        except (IOError, OSError) as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error serving {file_type}: {str(e)}'.encode())
            logger.error("Error serving %s: %s", file_type, e)
    
    def _serve_health_check(self):
        """Serve health check endpoint."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def _serve_status(self):
        """Serve status information."""
        epg_exists = self.epg_file_path and os.path.exists(self.epg_file_path)
        m3u_exists = self.m3u_file_path and os.path.exists(self.m3u_file_path)
        
        epg_size = os.path.getsize(self.epg_file_path) if epg_exists and self.epg_file_path else 0
        m3u_size = os.path.getsize(self.m3u_file_path) if m3u_exists and self.m3u_file_path else 0
        
        epg_mtime = os.path.getmtime(self.epg_file_path) if epg_exists and self.epg_file_path else 0
        m3u_mtime = os.path.getmtime(self.m3u_file_path) if m3u_exists and self.m3u_file_path else 0
        
        status = f"""HDHomeRun EPG to XMLTV Server Status

EPG File: {self.epg_file_path or 'Not configured'}
  Exists: {epg_exists}
  Size: {epg_size} bytes
  Last Modified: {epg_mtime}

M3U File: {self.m3u_file_path or 'Not configured'}
  Exists: {m3u_exists}
  Size: {m3u_size} bytes
  Last Modified: {m3u_mtime}

Available Endpoints:
  /epg.xml - XMLTV EPG data
  /channels.m3u - M3U playlist
  /health - Health check
  /status - This status page
"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-Length', str(len(status.encode())))
        self.end_headers()
        self.wfile.write(status.encode())
    
    def log_message(self, msg_format: str, *args) -> None:  # noqa: A002, ARG001
        """Override log_message to use Python logging."""
        logger.info(msg_format, *args)

def start_http_server(epg_file_path, m3u_file_path, bind_address='0.0.0.0', http_port=8000):
    """Start the HTTP server to serve the EPG and M3U files.
    
    Args:
        epg_file_path: Path to the EPG XML file to serve
        m3u_file_path: Path to the M3U playlist file to serve
        bind_address: Address to bind the server to (default: 0.0.0.0)
        http_port: Port to run the server on (default: 8000)
    """
    EPGRequestHandler.epg_file_path = epg_file_path
    EPGRequestHandler.m3u_file_path = m3u_file_path
    
    server_address = (bind_address, http_port)
    httpd = HTTPServer(server_address, EPGRequestHandler)
    
    logger.info("Starting HTTP server on %s:%d", bind_address, http_port)
    logger.info("EPG file path: %s", epg_file_path)
    logger.info("M3U file path: %s", m3u_file_path)
    logger.info("Access EPG at http://localhost:%d/epg.xml", http_port)
    logger.info("Access M3U at http://localhost:%d/channels.m3u", http_port)
    logger.info("Server status at http://localhost:%d/status", http_port)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("HTTP server stopped")
        httpd.shutdown()


if __name__ == '__main__':
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get configuration from environment or arguments
    epg_file = os.getenv('EPG_OUTPUT_FILE', '/app/output/epg.xml')
    m3u_file = os.getenv('M3U_OUTPUT_FILE', '/app/output/channels.m3u')
    bind_addr = os.getenv('HTTP_BIND_ADDRESS', '0.0.0.0')
    port = int(os.getenv('HTTP_PORT', '8000'))
    
    if len(sys.argv) > 1:
        epg_file = sys.argv[1]
    if len(sys.argv) > 2:
        m3u_file = sys.argv[2]
    if len(sys.argv) > 3:
        bind_addr = sys.argv[3]
    if len(sys.argv) > 4:
        port = int(sys.argv[4])
    
    start_http_server(epg_file, m3u_file, bind_addr, port)
