.PHONY: all clean build backend frontend zip

PLUGIN_NAME = rog-ally-rumble-fixer
VERSION = 1.0.3
BUILD_DIR = build
DIST_DIR = $(BUILD_DIR)/$(PLUGIN_NAME)
ZIP_NAME = $(PLUGIN_NAME)-$(VERSION).zip

all: build

build: backend frontend
	@echo "Building complete!"

backend:
	@echo "Building backend binary..."
	$(MAKE) -C backend
	@echo "Backend built successfully"

frontend:
	@echo "Building frontend..."
	pnpm install
	pnpm run build
	@echo "Frontend built successfully"

zip: build
	@echo "Creating distribution zip..."
	@rm -rf $(BUILD_DIR)
	@mkdir -p $(DIST_DIR)/bin
	@mkdir -p $(DIST_DIR)/dist
	
	@echo "Copying files..."
	@cp plugin.json $(DIST_DIR)/
	@cp package.json $(DIST_DIR)/
	@cp main.py $(DIST_DIR)/
	@cp README.md $(DIST_DIR)/
	@cp LICENSE $(DIST_DIR)/
	@cp dist/index.js $(DIST_DIR)/dist/
	@cp dist/index.d.ts $(DIST_DIR)/dist/ 2>/dev/null || true
	@cp backend/out/rumble-fixer $(DIST_DIR)/bin/
	
	@echo "Creating zip file..."
	@cd $(BUILD_DIR) && zip -r $(ZIP_NAME) $(PLUGIN_NAME)
	@echo "Created: $(BUILD_DIR)/$(ZIP_NAME)"
	@echo "Plugin size:"
	@ls -lh $(BUILD_DIR)/$(ZIP_NAME)

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@rm -rf dist
	@rm -rf node_modules
	@$(MAKE) -C backend clean
	@echo "Clean complete"

install: zip
	@echo "Installing to Decky plugins directory..."
	@mkdir -p $(HOME)/homebrew/plugins
	@rm -rf $(HOME)/homebrew/plugins/$(PLUGIN_NAME)
	@cp -r $(DIST_DIR) $(HOME)/homebrew/plugins/
	@echo "Installed to $(HOME)/homebrew/plugins/$(PLUGIN_NAME)/"
	@echo "Restart Decky Loader to see changes"
