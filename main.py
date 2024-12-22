import os
from PIL import Image
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from rembg import remove
from io import BytesIO

# Load environment variables
load_dotenv()

# Get the bot token
TOKEN = os.getenv("TOKEN")

# Create a directory for user images if it doesn't exist
USER_IMAGES_DIR = "user_images"
if not os.path.exists(USER_IMAGES_DIR):
    os.makedirs(USER_IMAGES_DIR)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome! Send me an image first, then use /logo_<your_command> to place Astrology LOGOs, or /change_background to change the background."
    )

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("-Simple Command to place all signs\n"
    "/logo_all_side : This puts 6 signs on the left and 6 on the right\n"
    "/logo_all_top : This puts 6 signs on top and 6 signs on bottom\n\n"
    "-You can put signs on the upper-left corner like a badge\n"
    "/logo_scorpio\n"
    "/logo_aries\n"
    "/logo_cancer\n"
    "/logo_capricorn\n"
    "/logo_virgo\n"
    "/logo_gemini\n"
    "/logo_aquarius\n"
    "/logo_libra\n"
    "/logo_pisces\n"
    "/logo_taurus\n"
    "/logo_sagittarius\n"
    "/logo_leo\n\n"
    "(It's possible put multiple signs as you want.)\n"
    "For example /logo_virgo_leo_cancer\n\n"
    "-Listed Signs:\n"
    "aries . cancer . capricorn . virgo . gemini . aquarius . libra . pisces . taurus . sagittarius . leo . scorpio \n\n"
    "-You can change background of your image with this command\n"
    "/change_background\n"
)
 

# Handle incoming images
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    
    # Get the image file
    photo = await update.message.photo[-1].get_file()
    
    # Create the file path
    file_path = os.path.join(USER_IMAGES_DIR, f"{user_id}.jpg")
    
    # Download and save the image
    await photo.download_to_drive(file_path)
    await update.message.reply_text(
        "Image received and stored! You can now use /help to explore commands."
    )

# Logo command handler
async def logo_handle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    bot_username = "@Astrology_Marker_Bot"
    if bot_username in text:
        text = text.replace(bot_username, "")
    
    user_id = str(update.effective_user.id)
    user_image_path = os.path.join(USER_IMAGES_DIR, f"{user_id}.jpg")
    
    if not os.path.exists(user_image_path):
        await update.message.reply_text(
            "Please send an image first before using the /logo command."
        )
        return
    
    image_directory = "./12MARKs"
    image_paths = get_image_paths(image_directory)
    image_count = len(image_paths)
    
    if "/logo" in text:
        await update.message.reply_text(f"An error occurred: {e}")

# Background change command handler
async def change_background(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    user_image_path = os.path.join(USER_IMAGES_DIR, f"{user_id}.jpg")
    background_image_path = os.path.join("", "0.jpg")
    
    if not os.path.exists(user_image_path):
        await update.message.reply_text(
            "Please send an image first before using the /change_background command."
        )
        return
    
    if not os.path.exists(background_image_path):
        await update.message.reply_text(
            "Background image (0.jpg) not found in the BACKs folder."
        )
        return
    
    try:
        updated_image = remove_background(user_image_path, background_image_path)
        output_path = os.path.join(USER_IMAGES_DIR, f"background_changed_{user_id}.jpg")
        updated_image.save(output_path)
        
        with open(output_path, "rb") as img_file:
            await update.message.reply_photo(photo=InputFile(img_file, filename="background_changed.jpg"))
        
        os.remove(output_path)
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")

# Helper function to remove background
def remove_background(user_image_path: str, background_image_path: str) -> Image.Image:
    with open(user_image_path, "rb") as user_image_file:
        user_image = remove(user_image_file.read())
    
    user_image = Image.open(BytesIO(user_image)).convert("RGBA")
    background_image = Image.open(background_image_path).convert("RGBA")
    background_image = background_image.resize(user_image.size)
    
    final_image = Image.alpha_composite(background_image, user_image)
    return final_image.convert("RGB")

# Helper function to get image paths
def get_image_paths(directory: str, allowed_extensions=("jpg", "png", "jpeg")):
    return [
        os.path.join(directory, filename)
        for filename in os.listdir(directory)
        if filename.endswith(allowed_extensions)
    ]

# Overlay images function
# [The overlay_images function remains unchanged]
def overlay_images(base_image_path, layout_type, image_paths, image_count):
    base_image = Image.open(base_image_path).convert('RGBA')
    base_width, base_height = base_image.size
    
    count = image_count
    if count % 2 == 1:
        count = count // 2 + 1
    else:
        count = count // 2
    
    # Initialize image_size and layout-specific variables
    image_size = None  # Default value to ensure it is always initialized
    padding = 0
    margin = 0
    
    if layout_type == "top":
        image_size = min(base_width // ((count + 1) * 6) * 5, base_height // 6)
        padding = image_size // 5
        margin = (base_width - (image_size * count + padding * (count + 1))) // 2 - padding
    elif layout_type == "side":
        image_size = min(base_height // ((count + 1) * 6) * 5, base_width // 6)
        padding = image_size // 5
        margin = (base_height - (image_size * count + padding * (count + 1))) // 2 - padding
    else:
        raise ValueError(f"Invalid layout type: {layout_type}. Use 'top' or 'side'.")
    
    # Resize images
    images = [Image.open(path).convert('RGBA').resize((image_size, image_size)) for path in image_paths]

    half = image_count // 2
    odd_image = None
    if image_count % 2 != 0:
        odd_image = images.pop()

    positions = []

    if layout_type == "top":
        positions_top = [(base_width // (half + 1) * (i + 1) - margin, padding) for i in range(half)]
        if odd_image:
            positions_top.append((base_width // (half + 1) * (half) - margin, padding))
        positions = positions_top
        positions_bottom = [(base_width // (half + 1) * (i + 1) - margin, base_height - image_size - padding) for i in range(len(images) - half)]
        positions.extend(positions_bottom)

    elif layout_type == "side":
        positions_left = [(padding, base_height // (half + 1) * (i + 1) - margin) for i in range(half)]
        if odd_image:
            positions_left.append((base_width - image_size - padding, base_height // (half + 1) * (half) - margin))
        positions = positions_left
        positions_right = [(base_width - image_size - padding, base_height // (len(images) - half + 1) * (i + 1) - margin) for i in range(len(images) - half)]
        positions.extend(positions_right)

    final_image = Image.new('RGBA', base_image.size, (0, 0, 0, 0))
    final_image.paste(base_image, (0, 0))

    for img, pos in zip(images + ([odd_image] if odd_image else []), positions):
        if img:
            temp = Image.new('RGBA', final_image.size, (0, 0, 0, 0))
            temp.paste(img, pos)
            final_image = Image.alpha_composite(final_image, temp)

    return final_image.convert('RGB')

# Main function
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("change_background", change_background))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, logo_handle))
    application.run_polling()

# Entry point
if __name__ == '__main__':
    main()
