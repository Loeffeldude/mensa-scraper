# HSBO Mensa Card PDF Downloader

Simple script to download your Mensa card PDF from the HSBO student portal.

## Usage

### Using Docker

Build the image

```bash
docker build -t hsbo-mensa-balance .
```

And run

```bash
docker run -e HSBO_USERNAME=your_username \
          -e HSBO_PASSWORD=your_password \
          -e HSBO_OUTPUTPATH=/path/to/output.pdf \
          -v /local/target/path/:/path/to/ \
          hsbo-mensa-balance
```

### Manual Run

```bash
poetry install
poetry run python main.py
```

## Configuration

Environment variables:

- `HSBO_USERNAME`: Your HSBO portal username
- `HSBO_PASSWORD`: Your HSBO portal password
- `HSBO_OUTPUTPATH`: Output path for PDF (use "-" for stdout)

The Docker container runs a daily download at 6:00 AM by default. Override with:

```bash
docker build --build-arg CRON="0 */6 * * *" -t hsbo-mensa-balance .
```
