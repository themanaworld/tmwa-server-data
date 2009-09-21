(*
 *  retab (c) 2009 The Mana World development team
 *  License: GPL, version 2 or later
 *
 *  Compilation, e.g. (depends on SML implementation):
 *    mlton retab.sml
 *
 *  Example usage:
 *    tools/retab < db/mob_db.txt > db/mob_db.txt.new && mv db/mob_db.txt.new db/mob_db.txt
 *
 *  TODO:
 *    - Commas inside {} need to be seen as just one field when tabified
 *    - Commented lines should be left untabified
 *)

fun width (#"\t", i)	= let val m = i mod 8 in if m = 0 then 8 else m end
  | width (c, i)	= 1

fun encode_width (offset) (l) =
    let fun expand ([], i)	= []
	  | expand (c::tl, i)	= let val w = width (c, i)
				  in (c, i, i + w) :: expand (tl, i + w)
				  end
    in expand (l, offset)
    end

fun strip_blanks (#" "::tl)	= strip_blanks (tl)
  | strip_blanks (#"\t"::tl)	= strip_blanks (tl)
  | strip_blanks (#"\n"::tl)	= strip_blanks (tl)
  | strip_blanks (#"\r"::tl)	= strip_blanks (tl)
  | strip_blanks (other)	= other

fun clean (s) = rev (strip_blanks (rev (strip_blanks (s))))

fun split_comma (#","::tl)	= [#","] :: (split_comma (strip_blanks (tl)))
  | split_comma ([])		= []
  | split_comma (h::tl)		= (case split_comma (tl) of
				       []	=> [[h]]
				     | (h'::tl)	=> (h::h')::tl
				  )

fun expand (l : char list list list, offset : int) : char list list list =
    if List.all (null) (l) (* at the end of all rows *)
    then l
    else let fun splitlist ([]::tl)		= let val (heads, tails) = splitlist (tl)
						  in ([]::heads, []::tails)
						  end
	       | splitlist ((hrow::tlrow)::tl)	= let val (heads, tails) = splitlist (tl)
						  in (hrow::heads, tlrow::tails)
						  end
	       | splitlist ([])			= ([], [])
	     val (heads, tails) = splitlist (l)
	     val eheads = map (encode_width offset) heads

	     fun last_offset []		= offset
	       | last_offset (cell)	= let val (_, _, x)::_ = rev (cell) in x end
	     val desired_final_offset = foldl Int.max offset (map last_offset (eheads))
(*
	     val () = print ("start offset = " ^ Int.toString (offset) ^ "\n")
	     val () = print ("FINAL OFFSET = " ^ Int.toString (desired_final_offset) ^ "\n")
*)
	     fun align (i) = ((i + 7) div 8) * 8
	     val desired_final_offset = align(desired_final_offset)
(*
	     val () = print ("FINAL OFFSET (align) = " ^ Int.toString (desired_final_offset) ^ "\n")
*)
	     fun fill (offset) = if offset >= desired_final_offset
				 then []
				 else #"\t" :: fill (align (offset - 7) + 8)
	     val fill = if List.all null tails
			then fn _ => []
			else fill
	     fun tabexpand ([])		= fill (offset)
	       | tabexpand (cell)	= let val (_, _, finalwidth)::_ = rev (cell)
					      fun strip (x, _, _) = x
					  in rev (fill (finalwidth) @ rev (map strip (cell)))
					  end
	     val expanded_heads = map tabexpand (eheads)
	     val expanded_tails = expand (tails, desired_final_offset)
	 in ListPair.map op:: (expanded_heads, expanded_tails)
	 end

fun align_strings (s : string list) = map (implode o List.concat) (expand (map ((map clean) o split_comma o explode) s, 0))

(*val test = align_strings (["foo, bar, quux", "a,b", "0,01234567890,c"])*)

fun println (s) = (print (s);
		   print "\n")

fun read_input () =
    case TextIO.inputLine (TextIO.stdIn) of
	NONE	=> []
      | SOME s	=> s :: read_input ()

fun main (_, _) = app println (align_strings (read_input ()))

val () = main ("", [])

