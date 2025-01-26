from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from eth_account import Account
from eth_account.messages import encode_defunct
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, random, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class MultipleLite:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Multiple Lite Node - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, private_key: str):
        try:
            account = Account.from_key(private_key)
            address = account.address
            
            return address
        except Exception as e:
            return None
    
    def generate_payload_data(self, account: str, address: str, timestamp: str, nonce: int):
        try:
            message = f"www.multiple.cc wants you to sign in with your Ethereum account: {address}\n\t     \nmessage:\nwebsite: www.multiple.cc\nwalletaddress: {address}\ntimestamp: {timestamp}\nNonce: {nonce}"
            encoded_message = encode_defunct(text=message)

            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = signed_message.signature.hex()

            data = {
                "walletAddr": address,
                "message": message,
                "signature": signature
            }

            return data
        except Exception as e:
            return None
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account
    
    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def dashboard_login(self, account: str, address: str, timestamp: str, nonce: int, proxy=None, retries=5):
        url = "https://api.app.multiple.cc/WalletLogin"
        data = json.dumps(self.generate_payload_data(account, address, timestamp, nonce))
        headers = {
            **self.headers,
            "Authorization": "Bearer",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Origin": "https://www.app.multiple.cc",
            "Referer": "https://www.app.multiple.cc/",
            "Sec-Fetch-Site": "same-site",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    timestamp = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    nonce = int(timestamp.timestamp() * 1000)
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"GET Dashboard Token Failed {Fore.YELLOW+Style.BRIGHT}{str(e)}")

    async def extension_login(self, account: str, address: str, dashboard_token: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.app.multiple.cc/ChromePlugin/Login"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {dashboard_token}",
            "Content-Length": '2',
            "Content-Type": "application/json",
            "Origin": "chrome-extension://ciljbjmmdhnhgbihlcohoadafmhikgib",
            "Sec-Fetch-Site": "none",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json={}) as response:
                        if response.status == 401:
                            dashboard_token = await self.get_dashboard_token(account, address, use_proxy)
                            headers["Authorization"] = f"Bearer {dashboard_token}"
                            continue
                            
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"GET Extension Token Failed {Fore.YELLOW+Style.BRIGHT}{str(e)}")
        
    async def user_information(self, account: str, address: str, extension_token: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.app.multiple.cc/ChromePlugin/GetInformation"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {extension_token}"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            dashboard_token = await self.get_extension_token(account, address, dashboard_token, use_proxy)
                            headers["Authorization"] = f"Bearer {extension_token}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                return self.print_message(address, proxy, Fore.RED, f"GET User Info Failed {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                
    async def send_keepalive(self, account: str, address: str, extension_token: str, use_proxy: bool, proxy=None, retries=5):
        url = "https://api.app.multiple.cc/ChromePlugin/KeepAlive"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {extension_token}",
            "Content-Length": '0',
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "chrome-extension://ciljbjmmdhnhgbihlcohoadafmhikgib",
            "Sec-Fetch-Site": "none",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers) as response:
                        if response.status == 401:
                            dashboard_token = await self.get_extension_token(account, address, dashboard_token, use_proxy)
                            headers["Authorization"] = f"Bearer {extension_token}"
                            continue

                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue

                self.print_message(address, proxy, Fore.RED, f"PING Failed {Fore.YELLOW+Style.BRIGHT}{str(e)}")
                proxy = self.rotate_proxy_for_account(account) if use_proxy else None
                return None
            
    async def get_user_information(self, account: str, address: str, extension_token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None
            user = await self.user_information(account, address, extension_token, use_proxy, proxy)
            if user:
                runing_time = user['totalRunningTime']
                is_online = user['isOnline']
                status = "Node Connected" if is_online else "Node Disconnected"
                formatted_time = self.format_seconds(runing_time)

                self.print_message(address, proxy, Fore.GREEN if is_online else Fore.RED,
                    f"{status} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Run Time: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{formatted_time}{Style.RESET_ALL}"
                )

            await asyncio.sleep(11 * 60)

    async def process_send_ping(self, account: str, address: str, extension_token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try To Send PING...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            
            ping = await self.send_keepalive(account, address, extension_token, use_proxy, proxy)
            if "success" in ping and ping['success']:
                self.print_message(address, proxy, Fore.GREEN, "PING Success")

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 10 Minutes For Next PING...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )

            await asyncio.sleep(10 * 60)

    async def get_dashboard_token(self, account: str, address: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(account) if use_proxy else None
        dashboard_token = None
        while dashboard_token is None:
            timestamp = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            nonce = int(timestamp.timestamp() * 1000)
            dashboard_token = await self.dashboard_login(account, address, timestamp, nonce, proxy)
            if not dashboard_token:
                proxy = self.rotate_proxy_for_account(account) if use_proxy else None
                continue
        
            self.print_message(address, proxy, Fore.GREEN, "GET Dashboard Token Success")
            return dashboard_token

    async def get_extension_token(self, account: str, address: str, dashboard_token: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(account) if use_proxy else None
        extension_token = None
        while extension_token is None:
            extension_token = await self.extension_login(account, address, dashboard_token, use_proxy, proxy)
            if not extension_token:
                proxy = self.rotate_proxy_for_account(account) if use_proxy else None
                continue
        
            self.print_message(address, proxy, Fore.GREEN, "GET Extension Token Success")
            return extension_token
        
    async def process_accounts(self, account: str, use_proxy: bool):
        address = self.generate_address(account)
        dashboard_token = await self.get_dashboard_token(account, address, use_proxy)
        if dashboard_token:
            extension_token = await self.get_extension_token(account, address, dashboard_token, use_proxy)
            if extension_token:
                
                tasks = []
                tasks.append(self.get_user_information(account, address, extension_token, use_proxy))
                tasks.append(self.process_send_ping(account, address, extension_token, use_proxy))
                await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        tasks.append(self.process_accounts(account, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = MultipleLite()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Multiple Lite Node - BOT{Style.RESET_ALL}                                       "                              
        )