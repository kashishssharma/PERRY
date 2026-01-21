# -*- coding: utf-8 -*-
# website_blocker.py
# Fixed Website Blocker with Proper Admin Handling and Cross-Platform Support

import os
import platform
import subprocess
import ctypes
from pathlib import Path
from datetime import datetime
import streamlit as st

class WebsiteBlocker:
    """
    Cross-platform website blocker that modifies the hosts file.
    Requires administrator/root privileges.
    """
    
    def __init__(self, blocked_sites=None):
        self.system = platform.system()
        self.blocked_sites = blocked_sites or [
            'youtube.com', 'www.youtube.com',
            'instagram.com', 'www.instagram.com',
            'facebook.com', 'www.facebook.com',
            'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
            'reddit.com', 'www.reddit.com',
            'netflix.com', 'www.netflix.com',
            'twitch.tv', 'www.twitch.tv',
            'tiktok.com', 'www.tiktok.com'
        ]
        
        # Determine hosts file path
        if self.system == 'Windows':
            self.hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
        else:  # Linux/Mac
            self.hosts_path = '/etc/hosts'
        
        self.redirect_ip = '127.0.0.1'
        self.marker_start = '# START FOCUS MODE BLOCKING'
        self.marker_end = '# END FOCUS MODE BLOCKING'
    
    def _check_admin_privileges(self):
        """Check if the script is running with admin/root privileges"""
        try:
            if self.system == 'Windows':
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:  # Linux/Mac
                return os.geteuid() == 0
        except Exception as e:
            st.error(f"Error checking admin privileges: {e}")
            return False
    
    def _read_hosts_file(self):
        """Read the hosts file content"""
        try:
            with open(self.hosts_path, 'r') as f:
                return f.readlines()
        except PermissionError:
            return None
        except Exception as e:
            st.error(f"Error reading hosts file: {e}")
            return None
    
    def _write_hosts_file(self, lines):
        """Write content to hosts file"""
        try:
            with open(self.hosts_path, 'w') as f:
                f.writelines(lines)
            return True
        except PermissionError:
            return False
        except Exception as e:
            st.error(f"Error writing to hosts file: {e}")
            return False
    
    def _flush_dns_cache(self):
        """Flush DNS cache to apply changes immediately"""
        try:
            if self.system == 'Windows':
                subprocess.run(['ipconfig', '/flushdns'], 
                             capture_output=True, 
                             check=False)
            elif self.system == 'Darwin':  # macOS
                subprocess.run(['sudo', 'dscacheutil', '-flushcache'], 
                             capture_output=True, 
                             check=False)
                subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], 
                             capture_output=True, 
                             check=False)
            else:  # Linux
                # Different methods for different Linux distros
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], 
                             capture_output=True, 
                             check=False)
            return True
        except Exception as e:
            # DNS flush failure is not critical
            return True
    
    def is_blocking_active(self):
        """Check if blocking is currently active"""
        lines = self._read_hosts_file()
        if lines is None:
            return False
        
        content = ''.join(lines)
        return self.marker_start in content
    
    def block_websites(self, enable_smart_blocking=True):
        """
        Block websites by adding entries to hosts file
        
        Args:
            enable_smart_blocking: If True, only blocks during focus sessions
        
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'blocked_sites': list,
                'requires_admin': bool
            }
        """
        # Check admin privileges first
        if not self._check_admin_privileges():
            return {
                'success': False,
                'message': 'Administrator/root privileges required',
                'blocked_sites': [],
                'requires_admin': True
            }
        
        # Read current hosts file
        lines = self._read_hosts_file()
        if lines is None:
            return {
                'success': False,
                'message': 'Cannot read hosts file (permission denied)',
                'blocked_sites': [],
                'requires_admin': True
            }
        
        # Check if already blocking
        if self.is_blocking_active():
            return {
                'success': True,
                'message': 'Blocking is already active',
                'blocked_sites': self.blocked_sites,
                'requires_admin': False
            }
        
        # Add blocking entries
        blocking_entries = [
            f'\n{self.marker_start}\n',
            f'# Added by Focus Timer on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        ]
        
        for site in self.blocked_sites:
            blocking_entries.append(f'{self.redirect_ip} {site}\n')
        
        blocking_entries.append(f'{self.marker_end}\n')
        
        # Write to hosts file
        lines.extend(blocking_entries)
        
        if not self._write_hosts_file(lines):
            return {
                'success': False,
                'message': 'Cannot write to hosts file (permission denied)',
                'blocked_sites': [],
                'requires_admin': True
            }
        
        # Flush DNS cache
        self._flush_dns_cache()
        
        return {
            'success': True,
            'message': f'Successfully blocked {len(self.blocked_sites)} websites',
            'blocked_sites': self.blocked_sites,
            'requires_admin': False
        }
    
    def unblock_websites(self):
        """
        Remove blocking entries from hosts file
        
        Returns:
            dict: {
                'success': bool,
                'message': str
            }
        """
        # Check admin privileges
        if not self._check_admin_privileges():
            return {
                'success': False,
                'message': 'Administrator/root privileges required'
            }
        
        # Read hosts file
        lines = self._read_hosts_file()
        if lines is None:
            return {
                'success': False,
                'message': 'Cannot read hosts file (permission denied)'
            }
        
        # Remove blocking section
        new_lines = []
        skip = False
        
        for line in lines:
            if self.marker_start in line:
                skip = True
                continue
            if self.marker_end in line:
                skip = False
                continue
            if not skip:
                new_lines.append(line)
        
        # Write back to hosts file
        if not self._write_hosts_file(new_lines):
            return {
                'success': False,
                'message': 'Cannot write to hosts file (permission denied)'
            }
        
        # Flush DNS cache
        self._flush_dns_cache()
        
        return {
            'success': True,
            'message': 'Successfully unblocked all websites'
        }
    
    def get_blocked_sites(self):
        """Get list of currently blocked sites"""
        return self.blocked_sites.copy()
    
    def add_site(self, site):
        """Add a site to the blocking list"""
        if site not in self.blocked_sites:
            self.blocked_sites.append(site)
            # Add www variant if not present
            www_site = f"www.{site}" if not site.startswith('www.') else site
            if www_site not in self.blocked_sites:
                self.blocked_sites.append(www_site)
    
    def remove_site(self, site):
        """Remove a site from the blocking list"""
        if site in self.blocked_sites:
            self.blocked_sites.remove(site)
        www_site = f"www.{site}" if not site.startswith('www.') else site
        if www_site in self.blocked_sites:
            self.blocked_sites.remove(www_site)


def show_admin_requirement():
    """Display instructions for running with admin privileges"""
    st.error("""
    ### = Administrator Privileges Required
    
    Website blocking requires administrator/root access to modify the system hosts file.
    
    **Windows:**
    1. Close this app
    2. Right-click on Command Prompt or Terminal
    3. Select "Run as Administrator"
    4. Navigate to your app directory
    5. Run: `streamlit run app2.py`
    
    **macOS/Linux:**
    1. Close this app
    2. Open Terminal
    3. Navigate to your app directory
    4. Run: `sudo streamlit run app2.py`
    5. Enter your password when prompted
    
    � **Note:** The app will function normally without blocking, but websites won't be blocked during focus sessions.
    """)


def show_website_blocking_warning(blocker):
    """Display active blocking warning"""
    st.warning(f"""
    ### =� Focus Mode Active - Distractions Blocked
    
    The following {len(blocker.get_blocked_sites())} sites are currently blocked:
    """)
    
    with st.expander("=� View Blocked Sites", expanded=False):
        blocked = blocker.get_blocked_sites()
        # Remove duplicates and www variants for display
        unique_sites = sorted(set([site.replace('www.', '') for site in blocked]))
        
        cols = st.columns(2)
        for idx, site in enumerate(unique_sites):
            with cols[idx % 2]:
                st.write(f" {site}")
    
    st.info("=� Close and reopen your browser for changes to take full effect!")


# Initialize blocker in session state
def get_website_blocker():
    """Get or create website blocker instance"""
    if 'website_blocker' not in st.session_state:
        # Default blocked sites if not imported from config
        default_blocked = [
            'youtube.com', 'www.youtube.com',
            'instagram.com', 'www.instagram.com',
            'facebook.com', 'www.facebook.com',
            'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
            'reddit.com', 'www.reddit.com',
            'netflix.com', 'www.netflix.com',
            'twitch.tv', 'www.twitch.tv',
            'tiktok.com', 'www.tiktok.com'
        ]
        st.session_state.website_blocker = WebsiteBlocker(blocked_sites=default_blocked)
    return st.session_state.website_blocker