"""
    MIT License

    Copyright (c) 2023 Radovan Draskovic

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from instaloader.instaloader import Instaloader
from instaloader.structures import Profile
import webbrowser
import requests
import time, sys, os

def loading_bar(iterable, total=None, prefix='', suffix='', length=30, fill='#', print_end='\r'):
    
    """
        Display a progress bar in the console.

        Parameters:
            iterable (iterable): An iterable object (e.g., list, range) to loop over.
            total (int, optional): Total number of iterations. If None, it will be inferred from the iterable's length.
            prefix (str, optional): Text to display before the loading bar.
            suffix (str, optional): Text to display after the loading bar.
            length (int, optional): Length of the loading bar in characters.
            fill (str, optional): Character used to fill the loading bar.
            print_end (str, optional): The character to print at the end of the loading bar (default is '\r' for carriage return).

        Returns:
            None
    """
    
    total = total or len(iterable)
    start_time = time.time()

    def format_time(seconds):
        minutes, seconds = divmod(int(seconds), 60)
        return f'{minutes:02d}:{seconds:02d}'

    for i, item in enumerate(iterable, 1):
        progress = i / total
        bar_length = int(length * progress)
        bar = fill * bar_length + '-' * (length - bar_length)
        elapsed_time = time.time() - start_time
        eta = (elapsed_time / i) * (total - i)
        sys.stdout.write(f'\r{prefix} [{bar}] {progress*100:.1f}% {suffix} Elapsed: {format_time(elapsed_time)}')
        sys.stdout.flush()
        yield item

    sys.stdout.write('\n')
    sys.stdout.flush()


def loadBar(pref="Progress: "):
    
    """
        Display a progress bar in the console.
    """
    
    items = list(range(100))
    for _ in loading_bar(items, prefix=pref, suffix='Completed', length=50):
        time.sleep(0.01)


def printProfileInformation(profile):
    
    """
        Called in order to print profile information consisting of:
            - Username
            - Full name
            - Is it private or not
            - Is it verified or not
            - Number of posts
            - How many followers the profile has
            - How many other profiles the specified one follow
            - Bio
    """
    
    print("        Username: ", profile.username)
    print("       Full Name: ", profile.full_name)
    print(" Private profile: ", profile.is_private)
    print("        Verified: ", profile.is_verified)
    print(" Number of Posts: ", profile.mediacount)
    print(" Followers Count: ", profile.followers)
    print(" Following Count: ", profile.followees)
    print("             Bio: ")
    print("\t\t------------")
    s = "\t\t"
    for letter in profile.biography:
        if letter != "\n":
            s += letter
        else:
            s = "\t\t\t"
    if s != "\t\t":
        print(s)
    print("\t\t------------")

    profilePicURL = profile.profile_pic_url
    ans = input("Do you want to see the profile picture (yes/no): ").lower()
    if ans == "yes":
        webbrowser.open_new_tab(profilePicURL)


def getImagesLinks(profile):
    
    """
        Store liks to every user's post in file. 
    """
    
    if profile.is_private:
        print("\tMESSAGE: Private profile! Cannot get links to posts!")
        return
    
    with open(profile.username + "LinksToPosts.txt", "w") as f:
        num = 1
        for post in profile.get_posts():
            if len(list(post.get_sidecar_nodes())) > 1:
                for sidecar_item in post.get_sidecar_nodes():
                    f.write(sidecar_item.display_url + "\n")
            else:
                f.write(post.url + "\n")
            sys.stdout.write(f'\r{"Link to post"} [{str(num) + "/" + str(profile.mediacount)}] {" written to file"}')
            sys.stdout.flush()
            num += 1
        sys.stdout.write(f'\r{"Link to post"} [{str(num) + "/" + str(profile.mediacount)}] {" written to file"}')
        sys.stdout.flush()
        sys.stdout.write('\n')
        sys.stdout.flush()
    print("Links stored in file: ", profile.username + "LinksToPosts.txt")


def download_content(url, download_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"Download complete: {download_path}")
    else:
        print(f"Failed to download content from: {url}")


def downloadPosts(profile):
    if profile.is_private:
        print("\tMESSAGE: Private profile! Cannot download posts!")
        return
    
    if not os.path.exists("./"+profile.username):
        os.mkdir("./" + profile.username)
    
    while(True):
        try:
            numberOfPosts = int(input("How many latest posts you want to download (Total number of posts: " + str(profile.mediacount) + "): "))
            if numberOfPosts <= 0 or numberOfPosts > profile.mediacount:
                continue
            else:
                break
        except:
            print()
            pass
    
    num = 1
    for post in profile.get_posts():
        if(num > numberOfPosts):
            break
        if not post.is_video:
            if len(list(post.get_sidecar_nodes())) > 1:
                additional = 1
                for sidecar_item in post.get_sidecar_nodes():
                    if not sidecar_item.is_video:
                        download_content(sidecar_item.display_url, "./" + profile.username + "/post_number_" + str(num) + str(additional) + ".png")
                        additional += 1
            else:
                download_content(post.url, "./" + profile.username + "/post_number_" + str(num) + ".png")
            num += 1
        else:
            print("Cannot download this post because it is not an image")


def downloadMostLikedPost(profile):
    if profile.is_private:
        print("\tMESSAGE: Private profile! Cannot download posts!")
        return
    
    print("Downloading post with the most likes. Might take some time.")
    if not os.path.exists("./"+profile.username):
        os.mkdir("./" + profile.username)
        
    mostLiked = -1
    url = ""
    
    for post in profile.get_posts():
        if(post.likes > mostLiked):
            mostLiked = post.likes
            url = post.url

    if mostLiked > -1:
        download_content(url, "./" + profile.username + "/mostLikedPost.png")
        print("Most liked post downloaded!")


def getTaggedPosts(profile):
    
    """
        This function creates a .txt file with links to posts where user is tagged on
    """
    
    if profile.is_private:
        print("\tMESSAGE: Private profile! Cannot download posts!")
        return
    count = 0
    with open("./" + profile.username + "TaggedPostLinks.txt", "w") as f:
        for post in profile.get_tagged_posts():
            f.write(post.url + "\n")
            count += 1
    
    if count > 0:
        print("Links stored in file: ", profile.username + "TaggedPostLinks.txt")
    else:
        print("No links available")
        os.unlink("./" + profile.username + "TaggedPostLinks.txt")


def loopOptions(profile, bot):
    
    while(True):
        
        print("\t\t\tChoose number in front of an option: ")
        print("\t\t\t\t#1 - Print profile information")
        print("\t\t\t\t#2 - Store post links in a file")
        print("\t\t\t\t#3 - Download images from a profile")
        print("\t\t\t\t#4 - Download most liked post")
        print("\t\t\t\t#5 - Store links to post where user is tagged")
        print("\t\t\t\t#6 - Choose different profile")
        print("\t\t\t\t-1 - Exit")
        
        try:
            inp = int(input("\t\t\tOption: "))
        
            if inp == 1:
                print("----------------------------------------------------------------------------------------")
                printProfileInformation(profile)
                print("----------------------------------------------------------------------------------------")
            elif inp == 2:
                print("----------------------------------------------------------------------------------------")
                getImagesLinks(profile)
                print("----------------------------------------------------------------------------------------")
            elif inp == 3:
                print("----------------------------------------------------------------------------------------")
                downloadPosts(profile)
                print("----------------------------------------------------------------------------------------")
            elif inp == 6:
                print("----------------------------------------------------------------------------------------")
                username = input("\tEnter username for search: ")
                try:
                    profile = Profile.from_username(bot.context, username)
                    loadBar("\tGetting user information: ")
                except:
                    print("\tMessage: Specified profile does not exist")
                    sys.exit(1)
                    
                print("----------------------------------------------------------------------------------------")
            elif inp == 4:
                print("----------------------------------------------------------------------------------------")
                downloadMostLikedPost(profile)
                print("----------------------------------------------------------------------------------------")
            elif inp == 5:
                print("----------------------------------------------------------------------------------------")
                getTaggedPosts(profile)
                print("----------------------------------------------------------------------------------------")
            elif inp == -1:
                print("----------------------------------------------------------------------------------------")
                print("Exiting...")
                print("----------------------------------------------------------------------------------------")
                break
            else:
                continue
        except:
            pass


def display_title():
    letters = {
        'A': ["  *  ", " * * ", "*****", "*   *", "*   *"],
        'C': [" ****", "*    ", "*    ", "*    ", " ****"],
        'E': ["*****", "*    ", "***  ", "*    ", "*****"],
        'G': [" ****", "*    ", "* ***", "*   *", " *** "],
        'I': ["*****", "  *  ", "  *  ", "  *  ", "*****"],
        'M': ["*   *", "** **", "* * *", "*   *", "*   *"],
        'N': ["*   *", "**  *", "* * *", "*  **", "*   *"],
        'P': ["****", "*  *", "****", "*   ", "*   "],
        'R': ["**** ", "*   *", "**** ", "* *  ", "*  **"],
        'S': [" ****", "*    ", " *** ", "    *", "**** "],
        'T': ["*****", "  *  ", "  *  ", "  *  ", "  *  "]
    }

    print("\t--------------------------------------------------------------------------------------------------")
    text = '   INSTAGRAM SCRAPER'
    for row in range(5):
        for char in text:
            if char != ' ':
                letter = letters[char][row]
                print(letter, end=" ")
            else:
                print(" ", end = "  ")
        print()
    print("\t--------------------------------------------------------------------------------------------------")


def main():
    
    display_title()
    
    bot = Instaloader()
    username = input("\tEnter username for search: ")
    
    try:
        profile = Profile.from_username(bot.context, username)
        loadBar("\tGetting user information: ")
    except:
        print("Message: Specified profile does not exist")
        sys.exit(1)

    loopOptions(profile, bot)
        
main()
