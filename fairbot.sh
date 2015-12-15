#!/bin/sh

# FAIRBOT script to create SQL for playing Fairwinds
#
# Copyright 2015, Berend M. Tober
#

me=$(basename $0)
tmp=".${me}.$$"
touch "${tmp}"
trap 'rm "${tmp}"' EXIT
export COLUMNS=10
unset file


syntax="
NAME
  ${me} - Interactive menu for the Fairwinds game. 

SYNOPSIS
  ${me} [options] host [username]  

DESCRIPTION
  ${me} is a script that presents an interactive menu system
  for playing the Fairwinds game hosted on the specified host.
  It requires that the psql data base client software be
  installed and accessible in the user's PATH.

  If no username is specified, it defaults to the current user.

  CTRL-D is used to exit menus.

OPTIONS

  -h
      Show help menu.

  -f file
      Save generated SQL statements to file instead of executing them.

"

if [ $# -lt 1 ]
then
  echo "${syntax}"
  exit
fi

while [ "$#" -gt 0 ]
do
  case $1 in
    -\?|-h)
      shift
      syntax
      exit
      ;;
    -f)
      file="${2}"
      shift 2
      ;;
    -*)
      echo "invalid option '${1}'"
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

fairian_name="${2-$USER}"
export PGDATABASE="fairwinds"
export PGHOST="${1}"
export PGUSER="${fairian_name}"

display_game_info="select click, start_time, end_time, click_interval from fairwinds;"
display_health_journal="select * from health_journal where fairian_name = current_user order by click;"
display_cash_journal="select * from cash_journal where fairian_name = current_user order by click;"
display_food_journal="select * from food_journal where fairian_name = current_user order by click;"
display_bonds="select * from bond where bond_owner = current_user or bond_issuer = current_user;"
display_land="select * from land where fairian_name = current_user;"
display_contracts="select * from work where customer = current_user or supplier = current_user;"
display_notes="select * from note where factor = current_user or debtor = current_user;"


function executemenu {
  if [[ -n "${file}" ]] 
  then
    echo "${sql}" >> "${file}"
  else
    sql="\set VERBOSITY terse
        ${1}"
    psql -q <<< "${sql}"
  fi
}

function createmenu {
  echo "Creating Fairian '${fairian_name}'"
  read -p "Player email address=" email

  sql="insert into fairian (fairian_name, passwd, email_address) values ('${fairian_name}', '${PGPASSWORD}', '${email}');"
  prompt="insert into fairian (fairian_name, passwd, email_address) values ('${fairian_name}', '******', '${email}');"
  export PGUSER="fairwinds"
  executemenu "${sql}" "${prompt}"
}

function labormenu {
  land_plots=$(psql -q -A -t <<< "select serial_number from land where fairian_name = current_user order by 1;")
  skills=$(psql -q -A -t <<< "select skill_name from skill order by 1;")

  unset fields values
  PS3="Select skill name "
  select skill_name in ${skills}
  do
    if [[ -n "${skill_name}" ]]
    then
      fields="${fields}, skill_name"
      values="${values}, '${skill_name}'"
    fi
    break
  done

  PS3="Select work place serial number "
  select work_place in ${land_plots}
  do
    if [[ -n "${work_place}" ]]
    then
      fields="${fields}, work_place"
      values="${values}, '${work_place}'"
    fi
    break
  done
  unset PS3

  fields="${fields#,}"
  values="${values#,}"
  sql="insert into work (${fields}) values (${values});"
  executemenu "${sql}"
}

function callmenu {
  notes=$(psql -q -A -t <<< "select serial_number from note where factor = current_user order by 1;")

  unset fields values
  PS3="Select note serial number "
  select note in ${notes}
  do
    [[ -z "${note}" ]] && break
    sql="update note set called = true where serial_number = '${note}';"
    executemenu "${sql}"
    break
  done
  unset PS3
}

function resignmenu {
  supplier_contracts=$(psql -q -A -t <<< "select contract_number from work where customer = current_user or supplier = current_user order by 1;")

  PS3="Select labor contract number "
  select contract_number in ${supplier_contracts}
  do
    [[ -z "${contract_number}" ]] && break
    sql="update work set active = false where contract_number = '${contract_number}';"
    executemenu "${sql}"
    break
  done
  unset PS3
}

function optionsmenu {
  case "${1}" in
    bond)
      read -p "bond term=" term
      if [[ -n "${term}" ]]
      then
        fields="${fields}, term"
        values="${values}, ${term}"
      fi
      ;;
    land)
      case "${2}" in
        bid)
          read -p "land productivity=" productivity
          if [[ -n "${productivity}" ]]
          then
            fields="${fields}, productivity"
            values="${values}, ${productivity}"
          fi
          ;;
        ask)
          read -p "land serial number=" serial_number
          if [[ -n "${serial_number}" ]]
          then
            fields="${fields}, serial_number"
            values="${values}, '${serial_number}'"
          fi
          ;;
      esac
      ;;
    work)
        read -p "contract term=" term
        if [[ -n "${term}" ]]
        then
          fields="${fields}, term"
          values="${values}, ${term}"
        fi
        
      case "${2}" in
        bid)
          read -p "minimum effectiveness=" effectiveness
          if [[ -n "${effectiveness}" ]]
          then
            fields="${fields}, effectiveness"
            values="${values}, ${effectiveness}"
          fi

          read -p "work place serial number=" work_place
          if [[ -n "${work_place}" ]]
          then
            fields="${fields}, work_place"
            values="${values}, '${work_place}'"
          fi
          ;;
      esac

      fields="${fields}, skill_name"
      values="${values}, 'farmer'"
      ;;
    food)
      read -p "quantity=" quantity
      if [[ -n "${quantity}" ]]
      then
        fields="${fields}, quantity"
        values="${values}, ${quantity}"
      fi
      ;;
    note)
      notes=$(psql -q -A -t <<< "select serial_number from note order by 1;")
      PS3="Select note serial number "
      select serial_number in ${notes}
      do
        fields="${fields}, serial_number"
        values="${values}, '${serial_number}'"
        break
      done
      unset PS3
  esac
    
  if [[ -z "${fields}" ]]
  then
    sql="insert into ${mrkt}_${side% - *} default values;"
  else
    sql="insert into ${mrkt}_${side% - *} (${fields##,}) values (${values##,});"
  fi
  executemenu "${sql}"
}


function sidemenu {
  sides=(
      "bid - Buy order" 
      "ask - Sell order"
      )
  unset side
  PS3="Buy (bid) or sell (ask)? "
  select side in "${sides[@]}"
  do
    case "${side% - *}" in
      "bid"|"ask")
        read -p "expiration=" expiration
        if [[ -n "${expiration}" ]]
        then
          fields="expiration"
          values="${expiration}"
        else
          fields=""
        fi

        read -p "price=" price
        if [[ -n "${price}" ]]
        then
          fields="${fields}, price"
          values="${values}, ${price}"
        fi
        ;;
      *)
        break 
        ;;
    esac
    optionsmenu ${mrkt} ${side% - *}
    break
  done
  unset PS3
}

function marketmenu {
  mrkts=("bond" "land" "work" "food" "note")
  unset mrkt
  PS3="Select market "
  select mrkt in "${mrkts[@]}"
  do
    case "${mrkt}" in
      "bond"|"land"|"work"|"food"|"note")
        sidemenu
        ;;
      *)
        break 
        ;;
    esac
    break
  done
  unset PS3
}

function reportsmenu {
  options=(
      "Game       - Display game information" 
      "Health     - Display health history journal"
      "Cash       - Display cash transcation journal"
      "Food       - Display food transcation journal"
      "Land       - Display owned land plots"
      "Bonds      - Display owned and issued bonds"
      "Contracts  - Display engaged labor contracts"
      "Notes      - Display factor/debtor notes")
  unset option
  select option in "${options[@]}"
  do
    option="${option%%[[:space:]]*- *}"

    case "${option}" in
      Game)
        sql="
        \C 'Game Information'
        ${display_game_info}
        \C
        "
        executemenu "${sql}" "${display_game_info}"
        ;;
      Health)
        sql="
        \C 'Recent Health Journal Entries'
        ${display_health_journal}
        \C
        "
        executemenu "${sql}" "${display_health_journal}"
        ;;
      Cash)
        sql="
        \C 'Recent Cash Journal Entries'
        ${display_cash_journal}
        \C
        "
        executemenu "${sql}" "${display_cash_journal}"
        ;;
      Food)
        sql="
        \C 'Recent Food Journal Entries'
        ${display_food_journal}
        \C
        "
        executemenu "${sql}" "${display_food_journal}"
        ;;
      Land)
        sql="
        \C 'Land'
        ${display_land}
        \C
        "
        executemenu "${sql}" "${display_land}"
        ;;
      Bonds)
        sql="
        \C 'Bonds'
        ${display_bonds}
        \C
        "
        executemenu "${sql}" "${display_bonds}"
        ;;
      Contracts)
        sql="
        \C 'Labor Contracts'
        ${display_contracts}
        \C
        "
        executemenu "${sql}" "${display_contracts}"
        ;;
      Notes)
        sql="
        \C 'Notes'
        ${display_notes}
        \C
        "
        executemenu "${sql}" "${display_notes}"
        ;;
      esac
  done

}

function mainmenu {
  options=(
      "Create     - Create a Fairian account named ${fairian_name}" 
      "Trade      - Enter buy/sell orders" 
      "Labor      - Assign self-owned labor contract" 
      "Terminate  - End a labor contract" 
      "Call       - Demand note payment" 
      "Reports    - Display game data"
      )
  unset option
  select option in "${options[@]}"
  do
    option="${option%%[[:space:]]*- *}"

    case "${option}" in
      "Create")
        createmenu
        ;;
      "Trade")
        marketmenu
        ;;
      "Labor")
        labormenu
        ;;
      "Terminate")
        resignmenu
        ;;
      "Call")
        callmenu
        ;;
      "Reports")
        reportsmenu
        ;;
      *)
        break 
        ;;
    esac
  done
  unset PS3
}

[[ -z "${PGPASSWORD}" ]] && read -s -p "Fairwinds password:" PGPASSWORD
echo
export PGPASSWORD
mainmenu


