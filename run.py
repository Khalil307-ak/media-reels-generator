#!/usr/bin/env python3
"""
Media Reels Generator - Main Entry Point
Processes media files and generates social media reels with highlights
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

from utils import (
    setup_logging, load_config, get_media_files, is_audio_file,
    is_video_file, validate_file, create_output_structure,
    create_highlight_folder, save_highlights_json, save_caption_file,
    get_file_duration
)
from transcribe import create_transcription_provider, detect_language
from highlight import HighlightExtractor
from editor import VideoEditor


def process_single_file(
    file_path: Path,
    config: dict,
    output_dir: str,
    num_highlights: int,
    target_language: Optional[str] = None,
    translate_to: Optional[str] = None,
    confirm_copyright: bool = False
) -> dict:
    """
    Process a single media file
    
    Args:
        file_path: Path to media file
        config: Configuration dictionary
        output_dir: Base output directory
        num_highlights: Number of highlights to extract
        target_language: Target language for transcription
        translate_to: Language to translate to (optional)
        confirm_copyright: Whether copyright confirmation is given
    
    Returns:
        Dictionary with processing results
    """
    logger = logging.getLogger("media_reels_generator")
    
    # Safety check
    safety_config = config.get('safety', {})
    if not confirm_copyright and safety_config.get('require_copyright_confirmation', False):
        logger.warning(f"Skipping {file_path.name}: Copyright confirmation required. Use --confirm-copyright flag.")
        return {'status': 'skipped', 'reason': 'copyright_confirmation_required'}
    
    # Validate file
    min_duration = safety_config.get('min_file_duration', 5.0)
    if not validate_file(file_path, min_duration):
        logger.warning(f"Skipping {file_path.name}: File too short or invalid")
        return {'status': 'skipped', 'reason': 'file_too_short'}
    
    logger.info(f"Processing: {file_path.name}")
    start_time = time.time()
    
    try:
        # Create output structure
        original_name = file_path.stem
        output_paths = create_output_structure(output_dir, original_name)
        
        # Determine if audio-only
        is_audio = is_audio_file(file_path)
        is_video = is_video_file(file_path)
        
        logger.info(f"File type: {'Audio' if is_audio else 'Video'}")
        
        # Step 1: Transcribe
        logger.info("Step 1: Transcribing audio...")
        transcription_config = config.get('transcription', {})
        provider_name = transcription_config.get('provider', 'openai')
        
        transcription_provider = create_transcription_provider(provider_name, config)
        
        # Detect or use specified language
        if target_language:
            transcribe_language = target_language
        else:
            # Auto-detect (will be done by transcription provider if not specified)
            transcribe_language = transcription_config.get('language')
        
        transcript_result = transcription_provider.transcribe(file_path, language=transcribe_language)
        
        detected_language = transcript_result.get('language', 'unknown')
        transcript_text = transcript_result['text']
        segments = transcript_result.get('segments', [])
        
        logger.info(f"Transcription complete. Language: {detected_language}, Segments: {len(segments)}")
        
        # Translation (if needed)
        if translate_to and translate_to != detected_language:
            logger.info(f"Translation requested: {detected_language} -> {translate_to}")
            # Translation would go here (using Google Translate API, etc.)
            # For now, we'll proceed with original language
            logger.warning("Translation not yet implemented. Using original language.")
        
        # Step 2: Extract highlights
        logger.info("Step 2: Extracting highlights...")
        highlights_config = config.get('highlights', {})
        min_duration = highlights_config.get('min_duration', 6.0)
        max_duration = highlights_config.get('max_duration', 60.0)
        
        extractor = HighlightExtractor(
            provider=highlights_config.get('llm_provider', 'openai'),
            model=highlights_config.get('llm_model', 'gpt-4o-mini'),
            api_key=config.get('api', {}).get('openai_api_key'),
            temperature=highlights_config.get('temperature', 0.3)
        )
        
        highlights = extractor.extract_highlights(
            transcript=transcript_text,
            segments=segments,
            num_highlights=num_highlights,
            min_duration=min_duration,
            max_duration=max_duration,
            language=detected_language
        )
        
        logger.info(f"Extracted {len(highlights)} highlights")
        
        # Step 3: Process highlights (extract clips, resize, create subtitles)
        logger.info("Step 3: Processing highlights...")
        editor = VideoEditor(config)
        
        processed_highlights = []
        
        for i, highlight in enumerate(highlights, 1):
            logger.info(f"Processing highlight {i}/{len(highlights)}")
            
            highlight_folder = create_highlight_folder(output_paths['base'], i)
            
            # Process video/audio clip
            try:
                result_paths = editor.process_highlight(
                    input_path=file_path,
                    highlight=highlight,
                    output_folder=highlight_folder,
                    is_audio_only=is_audio,
                    segments=segments
                )
                
                # Save caption file
                caption_path = highlight_folder / 'caption.txt'
                save_caption_file(
                    caption_path,
                    highlight.get('hook', 'Key highlight'),
                    highlight.get('summary', 'Important point.')
                )
                
                # Update highlight with file paths
                highlight['output_folder'] = str(highlight_folder)
                highlight['files'] = {
                    'base_clip': str(result_paths['base_clip']),
                    'srt': str(result_paths['srt']) if result_paths.get('srt') else None,
                    'resized': {k: str(v) for k, v in result_paths.get('resized', {}).items()}
                }
                
                processed_highlights.append(highlight)
                
            except Exception as e:
                logger.error(f"Failed to process highlight {i}: {e}")
                continue
        
        # Save highlights JSON
        save_highlights_json(output_paths['highlights_json'], processed_highlights)
        
        processing_time = time.time() - start_time
        logger.info(f"Processing complete in {processing_time:.2f}s: {file_path.name}")
        
        return {
            'status': 'success',
            'file': str(file_path),
            'highlights_count': len(processed_highlights),
            'processing_time': processing_time,
            'output_dir': str(output_paths['base'])
        }
    
    except Exception as e:
        logger.error(f"Error processing {file_path.name}: {e}", exc_info=True)
        return {
            'status': 'error',
            'file': str(file_path),
            'error': str(e)
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Media Reels Generator - Create social media reels from media files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single file
  python run.py --input video.mp4 --n-highlights 5
  
  # Process a folder
  python run.py --input ./media_folder --out ./outputs --n-highlights 3
  
  # Specify language and translation
  python run.py --input audio.mp3 --lang ar --translate-to en
  
  # Use local Whisper (set in config.yaml)
  python run.py --input video.mp4 --n-highlights 5
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Input file or folder containing media files'
    )
    
    parser.add_argument(
        '--out', '-o',
        type=str,
        default='outputs',
        help='Output directory (default: outputs)'
    )
    
    parser.add_argument(
        '--n-highlights', '-n',
        type=int,
        default=None,
        help='Number of highlights per file (default: from config)'
    )
    
    parser.add_argument(
        '--lang', '-l',
        type=str,
        default=None,
        help='Language code for transcription (e.g., ar, en, fr). Auto-detect if not specified.'
    )
    
    parser.add_argument(
        '--translate-to',
        type=str,
        default=None,
        help='Language code to translate to (optional)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--confirm-copyright',
        action='store_true',
        help='Confirm that you have rights to process the content'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Process multiple files in parallel'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    # Setup logging
    log_config = config.get('logging', {})
    logger = setup_logging(
        log_level=log_config.get('level', 'INFO'),
        log_file=log_config.get('log_file')
    )
    
    logger.info("=" * 60)
    logger.info("Media Reels Generator - Starting")
    logger.info("=" * 60)
    
    # Override config with CLI args
    if args.n_highlights:
        config['highlights']['default_count'] = args.n_highlights
    
    if args.parallel:
        config['output']['parallel_processing'] = True
    
    # Get media files
    try:
        media_files = get_media_files(args.input)
        logger.info(f"Found {len(media_files)} media file(s)")
    except Exception as e:
        logger.error(f"Error getting media files: {e}")
        sys.exit(1)
    
    # Process files
    results = []
    num_highlights = config['highlights']['default_count']
    
    if config['output'].get('parallel_processing', False) and len(media_files) > 1:
        logger.info("Processing files in parallel...")
        with ProcessPoolExecutor(max_workers=min(4, len(media_files))) as executor:
            futures = {
                executor.submit(
                    process_single_file,
                    file_path, config, args.out, num_highlights,
                    args.lang, args.translate_to, args.confirm_copyright
                ): file_path
                for file_path in media_files
            }
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
    else:
        logger.info("Processing files sequentially...")
        for file_path in media_files:
            result = process_single_file(
                file_path, config, args.out, num_highlights,
                args.lang, args.translate_to, args.confirm_copyright
            )
            results.append(result)
    
    # Summary
    logger.info("=" * 60)
    logger.info("Processing Summary")
    logger.info("=" * 60)
    
    successful = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') == 'error']
    skipped = [r for r in results if r.get('status') == 'skipped']
    
    logger.info(f"Total files: {len(results)}")
    logger.info(f"Successful: {len(successful)}")
    logger.info(f"Failed: {len(failed)}")
    logger.info(f"Skipped: {len(skipped)}")
    
    if successful:
        logger.info("\nSuccessfully processed files:")
        for r in successful:
            logger.info(f"  - {Path(r['file']).name}: {r['highlights_count']} highlights -> {r['output_dir']}")
    
    if failed:
        logger.warning("\nFailed files:")
        for r in failed:
            logger.warning(f"  - {Path(r['file']).name}: {r.get('error', 'Unknown error')}")
    
    if skipped:
        logger.info("\nSkipped files:")
        for r in skipped:
            logger.info(f"  - {Path(r['file']).name}: {r.get('reason', 'Unknown reason')}")
    
    logger.info("=" * 60)
    
    # Exit with error code if any failures
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()

